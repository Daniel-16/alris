"use client";

import { useState, useRef, useEffect, useCallback } from "react"; // Added useCallback
import { motion, AnimatePresence } from "framer-motion";
// import { BackgroundBeams } from "../components/BackgroundBeams";
import { FaPaperPlane, FaMicrophone } from "react-icons/fa";
import { IoInformationCircle } from "react-icons/io5";
// import NotLaunched from "../components/NotLaunched";
import ChatNavbar from "../components/ChatNavbar";
import ChatSidebar from "../components/ChatSidebar";
import { useAuth } from "../utils/AuthContext";
import VideoGrid from "@/components/VideoGrid";
import { getMessageLimits, updateMessageLimits } from "../actions/cookies";
import ProcessingMessage from "@/components/ProcessingMessage";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/cjs/styles/prism";
import TypingMessageRenderer from "../components/TypingMessageRenderer";

interface Message {
  type: "user" | "assistant";
  content: string;
  timestamp: string;
  video_urls?: string[];
}

const getApiUrl = () => {
  if (process.env.NEXT_PUBLIC_ENV === "development") {
    return "http://localhost:8000";
  }
  return process.env.NEXT_PUBLIC_API_URL;
};

const API_URL = getApiUrl();

export default function ChatPage() {
  const [isMobile, setIsMobile] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState("");
  const [showTooltip, setShowTooltip] = useState(false);
  const [showLimitTooltip, setShowLimitTooltip] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [remainingMessages, setRemainingMessages] = useState(5);
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const { user } = useAuth();
  const [isVideoCommand, setIsVideoCommand] = useState(false);
  const [typingMessageKey, setTypingMessageKey] = useState<string | null>(null);

  useEffect(() => {
    const initializeMessageLimits = async () => {
      try {
        const { lastResetTime, remainingMessages: storedMessages } =
          await getMessageLimits();

        if (lastResetTime) {
          const timeDiff = Date.now() - parseInt(lastResetTime);
          if (timeDiff >= 5 * 60 * 60 * 1000) {
            setRemainingMessages(5);
            await updateMessageLimits(5);
          } else if (storedMessages) {
            setRemainingMessages(parseInt(storedMessages));
          }
        } else {
          setRemainingMessages(5);
          await updateMessageLimits(5);
        }
      } catch (err) {
        setRemainingMessages(5);
        console.error("Error initializing message limits:", err);
      }
    };

    initializeMessageLimits();
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

  const scrollToBottom = useCallback(() => {
    if (chatContainerRef.current) {
      requestAnimationFrame(() => {
        if (chatContainerRef.current) {
          chatContainerRef.current.scrollTop =
            chatContainerRef.current.scrollHeight;
        }
      });
    }
  }, []);

  useEffect(() => {
    if (messages.length > 0) {
      scrollToBottom();
    }
  }, [messages, typingMessageKey, scrollToBottom]);

  useEffect(() => {
    if (process.env.NEXT_PUBLIC_ENV === "development") {
      console.log("Messages updated:", messages);
    }
  }, [messages]);

  const errorAlert = error && (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className="mb-4"
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
  );

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (
      e.key === "Enter" &&
      inputText.trim() &&
      !isProcessing &&
      !typingMessageKey
    ) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleTypingComplete = useCallback(() => {
    setTypingMessageKey(null);
  }, []);

  const handleSendMessage = async () => {
    if (!inputText.trim()) return;
    if (remainingMessages <= 0) {
      setError(
        "Message limit reached. Please wait 5 hours for your limit to reset."
      );
      return;
    }
    if (isProcessing || typingMessageKey) return;

    const videoRegex = /(youtube\.com|youtu\.be|play (a )?video|video)/i;
    setIsVideoCommand(videoRegex.test(inputText));

    const newMessage: Message = {
      type: "user",
      content: inputText,
      timestamp: new Date().toISOString() + "_user",
    };

    setMessages((prev) => [...prev, newMessage]);
    setInputText("");
    setIsProcessing(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/command`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ command: newMessage.content }),
      });

      const data = await response.json();
      setIsProcessing(false);

      if (data.type === "response") {
        const mainMessage = data.data;
        const newAssistantMessage: Message = {
          type: "assistant",
          content: mainMessage,
          timestamp: new Date().toISOString() + "_assistant",
          video_urls: data.video_urls,
        };
        setMessages((prev) => [...prev, newAssistantMessage]);
        setTypingMessageKey(newAssistantMessage.timestamp);

        const newValue = remainingMessages - 1;
        setRemainingMessages(newValue);
        await updateMessageLimits(newValue);
        setError(null);
      } else if (data.type === "error") {
        setError(
          data.message || "An error occurred while processing your request."
        );
        const errorAssistantMessage: Message = {
          type: "assistant",
          content:
            data.message || "An error occurred while processing your request.",
          timestamp: new Date().toISOString() + "_error",
        };
        setMessages((prev) => [...prev, errorAssistantMessage]);
        setTypingMessageKey(errorAssistantMessage.timestamp);
      }
    } catch (err) {
      setIsProcessing(false);
      const errorContent =
        "Failed to send message. Please check your internet connection or refresh the page.";
      setError(errorContent);
      const errorAssistantMessage: Message = {
        type: "assistant",
        content: errorContent,
        timestamp: new Date().toISOString() + "_catch_error",
      };
      setMessages((prev) => [...prev, errorAssistantMessage]);
      setTypingMessageKey(errorAssistantMessage.timestamp);
    }
  };

  return (
    <div className="relative min-h-screen bg-[#0A0A0F] text-white overflow-hidden">
      <ChatNavbar />
      <ChatSidebar />
      <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
      <div className="absolute inset-0 md:pl-64 flex flex-col mx-auto transition-all duration-300">
        <div className="fixed inset-0 pointer-events-none z-0">
          <div className="absolute right-0 w-[500px] h-[500px] bg-purple-900/20 rounded-full mix-blend-screen filter blur-[100px] opacity-70 animate-blob"></div>
          <div className="absolute left-20 w-[500px] h-[500px] bg-blue-900/20 rounded-full mix-blend-screen filter blur-[100px] opacity-70 animate-blob animation-delay-2000"></div>
        </div>

        <AnimatePresence>
          {messages.length === 0 && !isProcessing ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="flex flex-col items-center justify-center h-screen"
            >
              <h1 className="text-xl font-bold md:text-4xl md:font-medium mb-2 bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent">
                Hello {user?.user_metadata?.full_name || "there"}
              </h1>
              <h1 className="text-xl font-bold md:text-4xl md:font-medium mb-6 bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent">
                What can I do for you today?
              </h1>
              <div className="w-full max-w-[600px] px-4">
                {errorAlert}
                <form
                  className="relative"
                  onSubmit={(e) => {
                    e.preventDefault();
                    handleSendMessage();
                  }}
                >
                  <button
                    type="button"
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
                    onKeyDown={handleKeyDown}
                    placeholder={
                      isMobile
                        ? "Ask Alris..."
                        : "Ask Alris to 'Schedule a reminder' or 'Search for a video'"
                    }
                    className="w-full px-12 py-4 bg-[#1C1C27] text-white placeholder-gray-500 text-[15px] rounded-3xl focus:outline-none focus:ring-1 focus:ring-blue-500/50 transition-all"
                    disabled={isProcessing || !!typingMessageKey}
                  />
                  <button
                    type="submit"
                    disabled={
                      !inputText.trim() || isProcessing || !!typingMessageKey
                    }
                    className="absolute right-4 top-1/2 -translate-y-1/2 p-2 rounded-full transition-colors text-gray-400 hover:text-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <FaPaperPlane className="w-4 h-4" />
                  </button>
                </form>
              </div>
            </motion.div>
          ) : (
            <>
              <div
                ref={chatContainerRef}
                className="flex-1 overflow-y-auto md:px-15 px-4 mt-16 md:mx-10 h-[calc(100vh-200px)] pb-4"
              >
                {messages.map(
                  (
                    message
                  ) => (
                    <motion.div
                      key={message.timestamp}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3 }}
                      className={`flex flex-col ${
                        message.type === "user" ? "items-end" : "items-start"
                      } mb-4 w-full`}
                    >
                      <div
                        className={`max-w-[95%] md:max-w-[95%] ${
                          message.type === "user"
                            ? "bg-[#1C1C27] text-md text-white rounded-[30px] px-6 py-3 md:px-4 md:py-3"
                            : "text-white"
                        }`}
                      >
                        {message.type === "assistant" ? (
                          typingMessageKey === message.timestamp ? (
                            <TypingMessageRenderer
                              content={message.content}
                              onComplete={handleTypingComplete}
                              scrollToBottom={scrollToBottom}
                              typingSpeed={8}
                            />
                          ) : (
                            <div className="prose prose-invert max-w-none text-md break-words text-gray-200 leading-relaxed">
                              <ReactMarkdown
                                remarkPlugins={[remarkGfm]}
                                components={{
                                  code({
                                    node,
                                    className,
                                    children,
                                    ...props
                                  }) {
                                    const match = /language-(\w+)/.exec(
                                      className || ""
                                    );
                                    return !(props as any).inline && match ? (
                                      <SyntaxHighlighter
                                        style={oneDark}
                                        language={match[1]}
                                        PreTag="div"
                                        customStyle={{
                                          borderRadius: "0.5rem",
                                          padding: "1em",
                                          margin: "0.5em 0",
                                        }}
                                      >
                                        {String(children).replace(/\n$/, "")}
                                      </SyntaxHighlighter>
                                    ) : (
                                      <code className={className} {...props}>
                                        {children}
                                      </code>
                                    );
                                  },
                                }}
                              >
                                {message.content}
                              </ReactMarkdown>
                            </div>
                          )
                        ) : (
                          <p className="text-md md:text-sm text-white break-words">
                            {message.content}
                          </p>
                        )}
                      </div>
                      {message.type === "assistant" && message.video_urls && (
                        <VideoGrid videoUrls={message.video_urls} />
                      )}
                    </motion.div>
                  )
                )}
                {isProcessing && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex items-start mb-4 w-full"
                  >
                    {isVideoCommand ? (
                      <VideoGrid isLoading={true} />
                    ) : (
                      <ProcessingMessage />
                    )}
                  </motion.div>
                )}
              </div>

              <div className="sticky-bottom mb-4 w-full max-w-4xl px-4 mx-auto mt-2">
                {errorAlert}
                <form
                  className=""
                  onSubmit={(e) => {
                    e.preventDefault();
                    handleSendMessage();
                  }}
                >
                  <div className="h-24 md:h-28 bg-[#1C1C27] rounded-3xl overflow-hidden">
                    <input
                      type="text"
                      value={inputText}
                      onChange={(e) => setInputText(e.target.value)}
                      onKeyDown={handleKeyDown}
                      placeholder={
                        isMobile
                          ? "Ask Alris..."
                          : "Ask Alris to 'Schedule a reminder' or 'Search for a video'"
                      }
                      className="w-full py-3 px-8 md:py-4 bg-[#1C1C27] text-white placeholder-gray-500 text-[15px] transition-all"
                      style={{ outline: "none" }}
                      disabled={isProcessing || !!typingMessageKey}
                    />
                    <div className="relative top-8 md:top-6">
                      {" "}
                      <button
                        type="button"
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
                                className="absolute right-0 bottom-full mb-2 px-3 py-2 bg-gray-800 text-white text-sm rounded-lg whitespace-nowrap z-10"
                              >
                                {remainingMessages} message
                                {remainingMessages !== 1 ? "s" : ""} remaining
                                today
                              </motion.div>
                            )}
                          </AnimatePresence>
                        </div>
                      </div>
                      <button
                        type="submit"
                        disabled={
                          !inputText.trim() ||
                          isProcessing ||
                          !!typingMessageKey
                        }
                        className="absolute right-4 top-1/2 -translate-y-1/2 p-2 rounded-full transition-colors text-gray-400 hover:text-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <FaPaperPlane className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </form>
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
