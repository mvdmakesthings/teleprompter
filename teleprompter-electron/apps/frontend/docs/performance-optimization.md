# Performance Optimization Guide

This document describes the performance optimizations implemented in Phase 4.4 of the CueBird Electron refactor.

## Overview

The performance optimization system is designed to maintain 60 FPS smooth scrolling while handling large documents efficiently. It includes:

- Virtual scrolling for large texts
- React component optimization with memoization
- Request debouncing and caching
- Real-time performance monitoring
- Adaptive performance profiles

## Key Components

### 1. Virtual Scrolling

**Component**: `VirtualScroller.tsx`

Virtual scrolling is automatically enabled for texts larger than 10,000 words (configurable). It works by:

- Dividing content into chunks
- Rendering only visible chunks plus overscan
- Dynamically calculating chunk heights
- Maintaining scroll position accuracy

```tsx
// Automatic activation
const shouldUseVirtualScrolling = wordCount > perfConfig.virtualScrolling.wordThreshold
```

### 2. Optimized Components

All major components have been optimized with:

- `React.memo()` for preventing unnecessary re-renders
- `useCallback()` for stable function references
- `useMemo()` for expensive computations
- `useDeferredValue()` for non-critical updates
- `useTransition()` for concurrent features

**Optimized Components**:
- `OptimizedTeleprompterDisplay`
- `OptimizedControlPanel`
- `OptimizedFileLoader`

### 3. Request Optimization

**Component**: `optimized-api-client.ts`

The API client includes:

- Request debouncing (300ms default, 1s for settings)
- Response caching with TTL
- Exponential backoff for reconnection
- Concurrent request limiting

```tsx
// Example: Settings updates are debounced
await optimizedApiClient.updateSettings(settings) // Debounced by 1s
```

### 4. Performance Monitoring

**Component**: `PerformanceMonitor.tsx`

Real-time performance metrics:
- FPS tracking
- Frame drop detection
- Memory usage monitoring
- Render time measurement

The monitor appears in development mode and shows:
- Green: Optimal performance (55+ FPS)
- Yellow: Degraded performance (45-54 FPS)
- Red: Poor performance (<45 FPS)

### 5. Performance Profiles

**Configuration**: `performance-config.ts`

Three pre-configured profiles:

1. **High Performance** (for powerful machines)
   - 120 FPS target
   - Larger chunk sizes
   - More aggressive caching

2. **Balanced** (default)
   - 60 FPS target
   - Standard chunk sizes
   - Moderate caching

3. **Low Performance** (for older machines)
   - 30 FPS target
   - Smaller chunk sizes
   - GPU acceleration disabled

The system automatically detects the optimal profile based on:
- Available memory
- CPU cores
- GPU capabilities

## Usage

### Basic Usage

The optimizations are enabled by default. Simply use the optimized components:

```tsx
import { 
  OptimizedTeleprompterDisplay,
  OptimizedControlPanel,
  OptimizedFileLoader 
} from '@/components/teleprompter'

// Components automatically use performance optimizations
<OptimizedTeleprompterDisplay />
```

### Performance Context

Access performance configuration anywhere in the app:

```tsx
import { usePerformance } from '@/components/providers/performance-provider'

function MyComponent() {
  const { config, profile, setProfile } = usePerformance()
  
  // Switch to low performance mode
  setProfile('low')
  
  // Access configuration
  console.log(config.animation.targetFPS)
}
```

### Custom Configuration

Override specific settings:

```tsx
const { updateConfig } = usePerformance()

updateConfig({
  virtualScrolling: {
    wordThreshold: 5000, // Enable virtual scrolling earlier
  },
  animation: {
    targetFPS: 30, // Reduce target FPS
  }
})
```

## Performance Tips

1. **Large Documents**: Virtual scrolling automatically activates for documents >10k words
2. **Smooth Scrolling**: Maintained through RAF with frame time tracking
3. **Memory Management**: Unused chunks are unmounted to save memory
4. **GPU Acceleration**: Enabled by default for smooth animations
5. **Debouncing**: All settings updates are automatically debounced

## Monitoring Performance

In development mode, the performance monitor shows:
- Current FPS
- Frame drops
- Memory usage
- Render time

If performance degrades:
1. Check the performance monitor for bottlenecks
2. Consider switching to a lower performance profile
3. Reduce font size for very large documents
4. Close other applications to free resources

## Technical Details

### Frame Time Management

The scroll animation uses intelligent frame time management:

```tsx
const targetFrameTime = 1000 / perfConfig.animation.targetFPS
if (deltaTime < targetFrameTime) {
  // Skip frame to maintain target FPS
  return
}
```

### Throttling Strategy

Different operations use different throttle times:
- Scroll updates: 16ms (60 FPS)
- API requests: 300ms
- Settings updates: 1000ms

### Memory Optimization

- Virtual scrolling reduces DOM nodes
- Memoization prevents re-computations
- Deferred updates for non-critical changes
- Automatic garbage collection in low-performance mode

## Future Improvements

1. **Web Workers**: Offload markdown parsing to a worker thread
2. **Canvas Rendering**: Option to use canvas for extreme performance
3. **Predictive Loading**: Pre-render chunks before they're needed
4. **Adaptive Quality**: Dynamically adjust quality based on performance