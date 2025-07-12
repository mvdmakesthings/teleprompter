import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  output: 'export',
  // Disable image optimization for static export
  images: {
    unoptimized: true,
  },
  // Ensure trailing slashes for static export
  trailingSlash: true,
  // Configure base path if needed for Electron
  basePath: process.env.NODE_ENV === 'production' ? '' : '',
}

export default nextConfig