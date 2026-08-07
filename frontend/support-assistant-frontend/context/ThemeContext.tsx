"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode,
} from "react";

type Theme = "light" | "dark" | "system";
type FontSize = "small" | "medium" | "large";
type ChatWidth = "compact" | "comfortable" | "wide";

interface ThemeContextType {
  theme: Theme;
  setTheme: (theme: Theme) => void;

  fontSize: FontSize;
  setFontSize: (size: FontSize) => void;

  chatWidth: ChatWidth;
  setChatWidth: (width: ChatWidth) => void;

}

const ThemeContext = createContext<ThemeContextType | null>(null);

export function ThemeProvider({
  children,
}: {
  children: ReactNode;
}) {
  const [theme, setTheme] = useState<Theme>(() => {
    if (typeof window === "undefined") {
      return "dark";
    }

    const savedTheme = localStorage.getItem("theme");
    return savedTheme === "light" || savedTheme === "dark" || savedTheme === "system"
      ? savedTheme
      : "dark";
  });
  const [fontSize, setFontSize] = useState<FontSize>(() => {
    if (typeof window === "undefined") {
      return "medium";
    }

    const savedFont = localStorage.getItem("fontSize");
    return savedFont === "small" || savedFont === "medium" || savedFont === "large"
      ? savedFont
      : "medium";
  });
  const [chatWidth, setChatWidth] = useState<ChatWidth>(() => {
    if (typeof window === "undefined") {
      return "comfortable";
    }

    const savedWidth = localStorage.getItem("chatWidth");
    return savedWidth === "compact" || savedWidth === "comfortable" || savedWidth === "wide"
      ? savedWidth
      : "comfortable";
  });

  useEffect(() => {
    localStorage.setItem("theme", theme);
  }, [theme]);

  useEffect(() => {
    localStorage.setItem("fontSize", fontSize);
  }, [fontSize]);

  useEffect(() => {
    localStorage.setItem("chatWidth", chatWidth);
  }, [chatWidth]);


  return (
    <ThemeContext.Provider
    value={{
        theme,
        setTheme,

        fontSize,
        setFontSize,

        chatWidth,
        setChatWidth,
      }}
    >
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);

  if (!context) {
    throw new Error("useTheme must be inside ThemeProvider");
  }

  return context;
}