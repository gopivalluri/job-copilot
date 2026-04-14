/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `https://radiant-nourishment-production-a4b1.up.railway.app/:path*`,
      },
    ]
  },
}
module.exports = nextConfig
