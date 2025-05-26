"use client";

import React, { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/cjs/styles/prism";

interface TypingMessageRendererProps {
  content: string;
  onComplete: () => void;
  scrollToBottom: () => void;
  typingSpeed?: number;
}

export default function TypingMessageRenderer({
  content,
  onComplete,
  scrollToBottom,
  typingSpeed = 30,
}: TypingMessageRendererProps) {
  const [typedContent, setTypedContent] = useState("");
  const [currentIndex, setCurrentIndex] = useState(0);
  const [hasCompleted, setHasCompleted] = useState(false);

  useEffect(() => {
    setTypedContent("");
    setCurrentIndex(0);
    setHasCompleted(false);
  }, [content]);

  useEffect(() => {
    if (!hasCompleted && currentIndex < content.length) {
      const timeoutId = setTimeout(() => {
        setTypedContent((prev) => prev + content[currentIndex]);
        setCurrentIndex((prev) => prev + 1);
      }, typingSpeed);
      return () => clearTimeout(timeoutId);
    } else if (
      !hasCompleted &&
      currentIndex === content.length &&
      content.length > 0
    ) {
      if (typedContent.length === content.length) {
        onComplete();
        setHasCompleted(true);
      }
    } else if (!hasCompleted && content.length === 0) {
      onComplete();
      setHasCompleted(true);
    }
  }, [
    currentIndex,
    content,
    typedContent,
    typingSpeed,
    onComplete,
    hasCompleted,
  ]);

  useEffect(() => {
    if (typedContent) {
      scrollToBottom();
    }
  }, [typedContent, scrollToBottom]);

  return (
    <div className="prose prose-invert max-w-none text-md break-words text-gray-200 leading-relaxed">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          code({ node, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || "");
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
        {typedContent}
      </ReactMarkdown>
    </div>
  );
}
