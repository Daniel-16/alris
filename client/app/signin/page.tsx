"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { useState, useEffect, Suspense } from "react";
import { FaEye, FaEyeSlash, FaGoogle } from "react-icons/fa";
import { useAuth } from "../utils/AuthContext";
import { useRouter, useSearchParams } from "next/navigation";

function SignInContent() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const { signIn, signInWithGoogle } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const errorMessage = searchParams.get("error");
    if (errorMessage) {
      setError(decodeURIComponent(errorMessage));
    }
  }, [searchParams]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      await signIn(email, password);
      router.push("/chat");
    } catch (err: any) {
      console.error("Sign in error:", err);
      setError(err.message || "An error occurred during sign in");
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleSignIn = async () => {
    setError("");
    try {
      await signInWithGoogle();
    } catch (err: any) {
      console.error("Google sign in error:", err);
      setError(err.message || "An error occurred during Google sign in");
    }
  };

  return (
    <div className="min-h-screen overflow-hidden bg-[#0A0A0F] flex items-center justify-center">
      <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>

      <div className="absolute inset-0">
        <div className="absolute inset-0 opacity-50">
          <div className="fixed top-0 -left-32 w-96 h-96 bg-purple-600/20 rounded-full mix-blend-screen filter blur-[64px] animate-blob animation-delay-2000"></div>
          <div className="fixed bottom-0 -right-32 w-96 h-96 bg-blue-600/20 rounded-full mix-blend-screen filter blur-[64px] animate-blob"></div>
          <div className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-purple-600/20 rounded-full mix-blend-screen filter blur-[64px] animate-blob animation-delay-4000"></div>
        </div>
      </div>

      <div className="relative z-10 w-full max-w-md mx-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="bg-[#12121A] p-8 rounded-xl border border-purple-500/20"
        >
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold bg-gradient-to-r from-purple-600 via-blue-500 to-purple-600 bg-clip-text text-transparent">
              Welcome Back
            </h2>
            <p className="text-gray-400 mt-2">Sign in to continue to Alris</p>
          </div>

          {error && (
            <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/50 text-red-500">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Email address"
                className="w-full px-4 py-3 rounded-lg bg-[#1A1A23] border border-gray-700 text-white placeholder-gray-400 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                required
                disabled={isLoading}
              />
            </div>

            <div>
              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Password"
                  className="w-full px-4 py-3 rounded-lg bg-[#1A1A23] border border-gray-700 text-white placeholder-gray-400 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                  required
                  disabled={isLoading}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-300 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed"
                  disabled={isLoading}
                >
                  {showPassword ? <FaEyeSlash /> : <FaEye />}
                </button>
              </div>
            </div>

            {/* <div className="flex items-center justify-between text-sm">
              <label className="flex items-center text-gray-400">
                <input
                  type="checkbox"
                  className="mr-2 rounded border-gray-700 bg-[#1A1A23] disabled:opacity-50 disabled:cursor-not-allowed"
                  disabled={isLoading}
                />
                Remember me
              </label>
              <Link
                href="/forgot-password"
                className={`text-purple-500 hover:text-purple-400 ${
                  isLoading ? "pointer-events-none opacity-50" : ""
                }`}
                tabIndex={isLoading ? -1 : 0}
              >
                Forgot password?
              </Link>
            </div> */}

            <button
              type="submit"
              disabled={isLoading}
              className="w-full relative group disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span className="absolute inset-0 bg-gradient-to-r from-purple-600 via-blue-500 to-purple-600 blur-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300"></span>
              <span className="relative block px-8 py-3 md:py-3 md:font-medium md:px-10 rounded-xl border-2 border-transparent bg-gradient-to-r from-purple-600 via-blue-500 to-purple-600 bg-[length:200%_auto] animate-gradient hover:cursor-pointer">
                {isLoading ? "Signing in..." : "Sign In"}
              </span>
            </button>
          </form>

          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-700"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-[#12121A] text-gray-400">Or</span>
              </div>
            </div>

            <div className="mt-6 grid grid-cols-1 gap-4">
              <button
                onClick={handleGoogleSignIn}
                disabled={isLoading}
                className="flex items-center justify-center px-4 py-2 border border-gray-700 rounded-lg hover:border-gray-600 bg-[#1A1A23] text-gray-400 hover:text-gray-300 transition-all duration-300 hover:cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <FaGoogle className="mr-2" />
                Continue with Google
              </button>
            </div>
          </div>

          <p className="mt-8 text-center text-gray-400">
            Don't have an account?{" "}
            <Link
              href="/signup"
              className={`text-purple-500 hover:text-purple-400 ${
                isLoading ? "pointer-events-none opacity-50" : ""
              }`}
              tabIndex={isLoading ? -1 : 0}
            >
              Sign up
            </Link>
          </p>
        </motion.div>
      </div>

      <style jsx>{`
        @keyframes blob {
          0%,
          100% {
            transform: translate(0, 0) scale(1);
          }
          25% {
            transform: translate(20px, -30px) scale(1.1);
          }
          50% {
            transform: translate(-20px, 20px) scale(0.9);
          }
          75% {
            transform: translate(30px, 30px) scale(1.05);
          }
        }

        .animate-blob {
          animation: blob 20s infinite cubic-bezier(0.4, 0, 0.2, 1);
        }

        .animation-delay-2000 {
          animation-delay: 2s;
        }

        .animation-delay-4000 {
          animation-delay: 4s;
        }
      `}</style>
    </div>
  );
}

export default function SignIn() {
  return (
    <Suspense>
      <SignInContent />
    </Suspense>
  );
}
