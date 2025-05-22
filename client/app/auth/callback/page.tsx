"use client";

import { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { supabase } from "../../utils/supabase";
import { Suspense } from "react";
import { useAuth } from "../../utils/AuthContext";

function AuthCallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { setUser } = useAuth();

  useEffect(() => {
    const handleAuthCallback = async () => {
      try {
        const {
          data: { session },
          error,
        } = await supabase.auth.getSession();

        if (error) {
          console.error("Auth error:", error.message);
          router.push(`/signin?error=${encodeURIComponent(error.message)}`);
          return;
        }

        if (session) {
          const {
            data: { user },
          } = await supabase.auth.getUser();
          setUser(user ?? null);
          router.refresh();
          router.push("/chat");
        } else {
          router.push("/signin");
        }
      } catch (error) {
        console.error("Error during auth callback:", error);
        router.push("/signin");
      }
    };

    handleAuthCallback();
  }, [router, searchParams, setUser]);

  return (
    <div className="min-h-screen bg-[#0A0A0F] flex items-center justify-center">
      <div className="text-center">
        <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-gray-400">Completing authentication...</p>
      </div>
    </div>
  );
}

export default function AuthCallback() {
  return (
    <Suspense>
      <AuthCallbackContent />
    </Suspense>
  );
}
