"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { BackgroundBeams } from "../components/BackgroundBeams";
import { FaPaperPlane, FaMicrophone } from "react-icons/fa";
import { IoInformationCircle } from "react-icons/io5";
import NotLaunched from "../components/NotLaunched";
import ChatNavbar from "../components/ChatNavbar";
import ChatSidebar from "../components/ChatSidebar";
import { useAuth } from "../utils/AuthContext";
import getSocket, { sendMessage } from "@/lib/socket";
import VideoGrid from "@/components/VideoGrid";
import { getMessageLimits, updateMessageLimits } from "../actions/cookies";
// import { HiLink } from "react-icons/hi";

interface Message {
  type: "user" | "assistant";
  content: string;
  timestamp: string;
  video_urls?: string[];
}

export default function ChatPage() {
  const isProd = process.env.NODE_ENV === "production";
  const [isMobile, setIsMobile] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [showTooltip, setShowTooltip] = useState(false);
  const [showLimitTooltip, setShowLimitTooltip] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [remainingMessages, setRemainingMessages] = useState(3);
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const socketRef = useRef<WebSocket | null>(null);
  const { user } = useAuth();

  useEffect(() => {
    const initializeMessageLimits = async () => {
      try {
        const { lastResetTime, remainingMessages: storedMessages } =
          await getMessageLimits();

        if (lastResetTime) {
          const timeDiff = Date.now() - parseInt(lastResetTime);
          if (timeDiff >= 24 * 60 * 60 * 1000) {
            setRemainingMessages(3);
            await updateMessageLimits(3);
          } else if (storedMessages) {
            setRemainingMessages(parseInt(storedMessages));
          }
        } else {
          await updateMessageLimits(3);
        }
      } catch (err) {
        console.error("Error initializing message limits:", err);
      }
    };

    initializeMessageLimits();
  }, []);

  useEffect(() => {
    const socket = getSocket();
    socketRef.current = socket;

    socket.onopen = () => {
      setIsConnected(true);
      setError(null);
    };

    socket.onclose = () => {
      setIsConnected(false);
      setError(
        "Connection lost. Please check your internet connection and try again."
      );
    };

    socket.onerror = () => {
      setError("Unable to connect to the server. Please try again later.");
    };

    socket.onmessage = (event) => {
      try {
        const response = JSON.parse(event.data);
        if (response.type === "response") {
          const mainMessage = response.data.split("\n")[0];
          const newMessage: Message = {
            type: "assistant",
            content: mainMessage,
            timestamp: new Date().toISOString(),
            video_urls: response.video_urls,
          };
          setMessages((prev) => [...prev, newMessage]);
          setIsProcessing(false);
          setError(null);
        } else if (response.type === "error") {
          console.error("Server error:", response.message);
          setError(
            response.message ||
              "An error occurred while processing your request."
          );
          setIsProcessing(false);
        }
      } catch (error) {
        console.error("Error parsing message:", error);
        setError("Something went wrong. Please try again.");
        setIsProcessing(false);
      }
    };

    return () => {
      if (socket) {
        socket.close();
      }
    };
  }, []);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };

    checkMobile();
    window.addEventListener("resize", checkMobile);
    return () => window.removeEventListener("resize", checkMobile);
  }, []);

  useEffect(() => {
    if (showTooltip) {
      const timer = setTimeout(() => {
        setShowTooltip(false);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [showTooltip]);

  const scrollToBottom = () => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop =
        chatContainerRef.current.scrollHeight;
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // if (isProd) {
  //   return (
  //     <>
  //       <ChatNavbar />
  //       <NotLaunched />
  //     </>
  //   );
  // }

  const handleSendMessage = async () => {
    if (!inputText.trim()) return;
    if (!isConnected) {
      setError("Not connected to server. Please wait or refresh the page.");
      return;
    }
    if (remainingMessages <= 0) {
      setError(
        "Message limit reached. Please wait 24 hours for your limit to reset."
      );
      return;
    }

    const newMessage: Message = {
      type: "user",
      content: inputText,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, newMessage]);
    setIsProcessing(true);
    setError(null);

    const newValue = remainingMessages - 1;
    setRemainingMessages(newValue);

    try {
      await updateMessageLimits(newValue);
      sendMessage(inputText);
      setInputText("");
      setTimeout(scrollToBottom, 100);
    } catch (err) {
      setError("Failed to send message. Please try again.");
      setIsProcessing(false);
    }
  };

  return (
    <div className="relative min-h-screen bg-[#0A0A0F] text-white overflow-hidden">
      <ChatNavbar />
      <ChatSidebar isMobile={isMobile} />
      <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
      {/* <BackgroundBeams className="opacity-20" /> */}
      <div className="absolute inset-0 md:pl-64 flex flex-col mx-auto transition-all duration-300">
        <div className="absolute inset-0 md:pl-64 transition-all duration-300">
          <div className="absolute inset-0 opacity-30">
            <div className="fixed top-0 -left-20 w-96 h-96 bg-purple-900/30 rounded-full mix-blend-screen filter blur-[64px] animate-blob animation-delay-2000"></div>
            <div className="fixed bottom-0 -right-0 w-96 h-96 bg-blue-900/30 rounded-full mix-blend-screen filter blur-[64px] animate-blob"></div>
            <div className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-purple-900/30 rounded-full mix-blend-screen filter blur-[64px] animate-blob animation-delay-4000"></div>
          </div>
        </div>

        <AnimatePresence>
          {messages.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="flex flex-col items-center justify-center h-screen"
            >
              <h1 className="text-xl font-bold md:text-4xl md:font-medium mb-2 bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent">
                Hello {user?.user_metadata?.full_name}
              </h1>
              <h1 className="text-xl font-bold md:text-4xl md:font-medium mb-6 bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent">
                What can I do for you today?
              </h1>
              <div className="w-full max-w-[600px] px-4">
                <div className="relative">
                  <button
                    onClick={() => setShowTooltip(true)}
                    className="absolute left-4 top-1/2 -translate-y-1/2 p-2 rounded-full transition-colors text-gray-400 opacity-50 cursor-not-allowed"
                  >
                    <FaMicrophone className="w-4 h-4" />
                  </button>
                  <AnimatePresence>
                    {showTooltip && (
                      <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 10 }}
                        className="absolute left-0 bottom-full mb-2 px-3 py-2 bg-gray-800 text-white text-sm rounded-lg whitespace-nowrap"
                      >
                        Voice command is not activated as of now
                      </motion.div>
                    )}
                  </AnimatePresence>
                  <input
                    type="text"
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    placeholder="Play a youtube video"
                    className="w-full px-12 py-4 bg-[#1C1C27] text-white placeholder-gray-500 text-[15px] rounded-4xl focus:outline-none focus:ring-1 focus:ring-blue-500/50 transition-all"
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault();
                        handleSendMessage();
                      }
                    }}
                  />
                  <button
                    onClick={handleSendMessage}
                    disabled={!inputText.trim()}
                    className="absolute right-4 top-1/2 -translate-y-1/2 p-2 rounded-full transition-colors text-gray-400 hover:text-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <FaPaperPlane className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </motion.div>
          ) : (
            <>
              <div
                ref={chatContainerRef}
                className="flex-1 overflow-y-auto px-4 mt-16 custom-scrollbar"
                style={{
                  overflowY: "auto",
                  overscrollBehaviorY: "contain",
                  height: "calc(100vh - 200px)",
                }}
              >
                {error && (
                  <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-4 w-full"
                  >
                    <div className="bg-red-500/10 border border-red-500/20 rounded-lg px-4 py-3 flex items-start">
                      <div className="flex-shrink-0 mt-0.5">
                        <svg
                          className="h-5 w-5 text-red-500"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                        >
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                            clipRule="evenodd"
                          />
                        </svg>
                      </div>
                      <div className="ml-3">
                        <p className="text-sm text-red-500">{error}</p>
                      </div>
                    </div>
                  </motion.div>
                )}
                {messages.map((message, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                    className={`flex flex-col ${
                      message.type === "user" ? "items-end" : "items-start"
                    } mb-4 w-full`}
                  >
                    <div
                      className={`max-w-[95%] md:max-w-[80%] rounded-full px-3 py-2 md:px-4 md:py-4 ${
                        message.type === "user" ? "bg-blue-500" : "bg-[#1C1C27]"
                      }`}
                    >
                      <p className="text-[13px] md:text-sm text-white">
                        {message.content}
                      </p>
                    </div>
                    {message.type === "assistant" && message.video_urls && (
                      <VideoGrid videoUrls={message.video_urls} />
                    )}
                  </motion.div>
                ))}
                {isProcessing && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex items-start mb-4 w-full"
                  >
                    <div className="max-w-[95%] md:max-w-[80%] rounded-full px-3 py-2 md:px-4 md:py-4 bg-[#1C1C27]">
                      <div className="flex items-center space-x-1.5 md:space-x-2">
                        <div
                          className="w-1.5 h-1.5 md:w-2 md:h-2 bg-blue-500 rounded-full animate-bounce"
                          style={{ animationDelay: "0s" }}
                        ></div>
                        <div
                          className="w-1.5 h-1.5 md:w-2 md:h-2 bg-blue-500 rounded-full animate-bounce"
                          style={{ animationDelay: "0.2s" }}
                        ></div>
                        <div
                          className="w-1.5 h-1.5 md:w-2 md:h-2 bg-blue-500 rounded-full animate-bounce"
                          style={{ animationDelay: "0.4s" }}
                        ></div>
                      </div>
                    </div>
                  </motion.div>
                )}
              </div>

              <div className="sticky-bottom mb-4 w-full max-w-4xl px-4 mx-auto">
                <div className="relative">
                  <button
                    onClick={() => setShowTooltip(true)}
                    className="absolute left-4 top-1/2 -translate-y-1/2 p-2 rounded-full transition-colors text-gray-400 opacity-50 cursor-not-allowed"
                  >
                    <FaMicrophone className="w-4 h-4" />
                  </button>
                  <div className="absolute right-12 top-1/2 -translate-y-1/2 flex items-center">
                    <div
                      className="relative"
                      onMouseEnter={() => setShowLimitTooltip(true)}
                      onMouseLeave={() => setShowLimitTooltip(false)}
                    >
                      <div className="flex items-center gap-1 text-gray-400">
                        <IoInformationCircle className="w-4 h-4" />
                        <span className="text-sm">{remainingMessages}</span>
                      </div>
                      <AnimatePresence>
                        {showLimitTooltip && (
                          <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: 10 }}
                            className="absolute right-0 bottom-full mb-2 px-3 py-2 bg-gray-800 text-white text-sm rounded-lg whitespace-nowrap"
                          >
                            {remainingMessages} message
                            {remainingMessages !== 1 ? "s" : ""} remaining today
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>
                  </div>
                  <input
                    type="text"
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    placeholder="Play a youtube video"
                    className="w-full py-3 px-12 md:py-4 bg-[#1C1C27] text-white placeholder-gray-500 text-[15px] rounded-4xl focus:outline-none focus:ring-1 focus:ring-blue-500/50 transition-all"
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault();
                        handleSendMessage();
                      }
                    }}
                  />
                  <button
                    onClick={handleSendMessage}
                    disabled={!inputText.trim()}
                    className="absolute right-4 top-1/2 -translate-y-1/2 p-2 rounded-full transition-colors text-gray-400 hover:text-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <FaPaperPlane className="w-4 h-4" />
                  </button>
                </div>
                <p className="text-xs text-gray-500 mt-2 text-center">
                  Alris can make mistakes. Check for verification of content.
                </p>
              </div>
            </>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
