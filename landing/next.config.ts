import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // On Vercel we run Next.js natively (the "/" route is still prerendered as
  // static). `output: "export"` is only needed for non-Vercel static hosts and
  // breaks routing on Vercel, so it is intentionally not set here.
  turbopack: { root: __dirname },
};

export default nextConfig;
