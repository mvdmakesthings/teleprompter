"""WebSocket handler for audio streaming and voice detection."""

import json
import numpy as np
from fastapi import WebSocket, WebSocketDisconnect

from ....core.container import get_container
from ...services.voice_adapter import VoiceDetectorAdapter
from ..models import WebSocketMessage, VoiceActivity


class AudioWebSocketHandler:
    """Handler for audio streaming WebSocket connections."""
    
    def __init__(self):
        """Initialize the audio WebSocket handler."""
        self.voice_detectors: dict[WebSocket, VoiceDetectorAdapter] = {}
        self.audio_configs: dict[WebSocket, dict] = {}
    
    async def handle_connection(self, websocket: WebSocket):
        """Handle an audio WebSocket connection."""
        await websocket.accept()
        
        # Create a voice detector for this connection
        voice_detector = VoiceDetectorAdapter(
            on_voice_activity=lambda activity: self._send_voice_activity(websocket, activity)
        )
        self.voice_detectors[websocket] = voice_detector
        
        try:
            while True:
                # Receive data (can be text or binary)
                data = await websocket.receive()
                
                if 'text' in data:
                    # Handle text messages (configuration, commands)
                    await self._handle_text_message(websocket, data['text'])
                elif 'bytes' in data:
                    # Handle binary audio data
                    await self._handle_audio_data(websocket, data['bytes'])
        
        except WebSocketDisconnect:
            await self._cleanup_connection(websocket)
        except Exception as e:
            print(f"Audio WebSocket error: {e}")
            await self._cleanup_connection(websocket)
    
    async def _handle_text_message(self, websocket: WebSocket, message: str):
        """Handle text messages from the WebSocket."""
        try:
            data = json.loads(message)
            msg_type = data.get('type')
            
            if msg_type == 'config':
                # Store audio configuration
                self.audio_configs[websocket] = {
                    'sampleRate': data.get('sampleRate', 16000),
                    'frameSize': data.get('frameSize', 2048),
                    'frameDuration': data.get('frameDuration', 30),
                }
                
                # Start voice detection
                voice_detector = self.voice_detectors.get(websocket)
                if voice_detector:
                    voice_detector.start()
            
            elif msg_type == 'sensitivity':
                # Update sensitivity
                sensitivity = data.get('sensitivity', 2)
                voice_detector = self.voice_detectors.get(websocket)
                if voice_detector:
                    voice_detector.set_sensitivity(sensitivity)
            
            elif msg_type == 'stop':
                # Stop voice detection
                voice_detector = self.voice_detectors.get(websocket)
                if voice_detector:
                    voice_detector.stop()
        
        except json.JSONDecodeError:
            print(f"Invalid JSON received: {message}")
        except Exception as e:
            print(f"Error handling text message: {e}")
    
    async def _handle_audio_data(self, websocket: WebSocket, audio_bytes: bytes):
        """Handle binary audio data from the WebSocket."""
        try:
            # Convert bytes to numpy array (expecting Int16)
            audio_data = np.frombuffer(audio_bytes, dtype=np.int16)
            
            # Get audio configuration
            config = self.audio_configs.get(websocket, {})
            sample_rate = config.get('sampleRate', 16000)
            
            # Process audio through voice detector
            voice_detector = self.voice_detectors.get(websocket)
            if voice_detector and hasattr(voice_detector, 'process_audio_chunk'):
                # Process the audio chunk
                voice_detector.process_audio_chunk(audio_data, sample_rate)
            else:
                # If the voice detector doesn't support streaming, we'll need to buffer
                # For now, just calculate audio level
                audio_float = audio_data.astype(np.float32) / 32768.0
                audio_level = float(np.abs(audio_float).mean())
                
                # Send audio level update
                await websocket.send_json({
                    'type': 'voice_activity',
                    'is_active': audio_level > 0.02,  # Simple threshold
                    'audio_level': audio_level,
                })
        
        except Exception as e:
            print(f"Error processing audio data: {e}")
    
    async def _send_voice_activity(self, websocket: WebSocket, activity: VoiceActivity):
        """Send voice activity update to the client."""
        try:
            await websocket.send_json({
                'type': 'voice_activity',
                'is_active': activity.is_speaking,
                'audio_level': activity.audio_level,
                'state': activity.state.value,
            })
        except Exception as e:
            print(f"Error sending voice activity: {e}")
    
    async def _cleanup_connection(self, websocket: WebSocket):
        """Clean up resources for a disconnected WebSocket."""
        # Stop and remove voice detector
        voice_detector = self.voice_detectors.pop(websocket, None)
        if voice_detector:
            voice_detector.stop()
        
        # Remove audio configuration
        self.audio_configs.pop(websocket, None)
        
        # Close the WebSocket
        try:
            await websocket.close()
        except Exception:
            pass


# Global instance
audio_ws_handler = AudioWebSocketHandler()