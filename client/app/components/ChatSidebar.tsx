"use client";

import * as React from "react";
import { useAuth } from "../utils/AuthContext";
import { FaYoutube, FaGoogleDrive } from "react-icons/fa";
import {
  Sidebar,
  SidebarContent,
  SidebarProvider,
  SidebarTrigger,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarFooter,
} from "@/components/ui/sidebar";
import { ChevronsUpDown, Menu, PanelLeft } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface ChatSidebarProps {
  isMobile?: boolean;
}

const ChatSidebar = ({ isMobile = false }: ChatSidebarProps) => {
  const { signOut, user, linkTwitter, isTwitterConnected } = useAuth();
  console.log("[DEBUG] Current user:", user);
  if (user?.identities) {
    console.log("[DEBUG] User identities:", user.identities);
  }

  return (
    <SidebarProvider defaultOpen={!isMobile}>
      {isMobile && (
        <SidebarTrigger className="fixed top-4 left-4 z-50">
          <Menu className="w-6 h-6 text-gray-400" />
        </SidebarTrigger>
      )}
      <Sidebar className="">
        <SidebarContent>
          <SidebarGroup>
            <SidebarGroupLabel className="text-gray-400 mt-2 px-3 font-bold mb-2 text-xl">
              Tools
            </SidebarGroupLabel>
            <div className="h-[1px] bg-gray-700/50 my-2 mx-3"></div>
            <SidebarMenu>
              <SidebarMenuItem className="mb-2">
                <SidebarMenuButton className="bg-blue-500/10" isActive>
                  <FaYoutube className="w-4 h-4 text-red-500" />
                  <span className="text-gray-300">YouTube</span>
                  <span className="ml-auto text-[10px] font-medium px-2 py-0.5 rounded-full bg-green-500 text-black">
                    Active
                  </span>
                </SidebarMenuButton>
              </SidebarMenuItem>

              <SidebarMenuItem className="mb-2">
                <SidebarMenuButton>
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    x="0px"
                    y="0px"
                    width="100"
                    height="100"
                    viewBox="0 0 48 48"
                  >
                    <path
                      fill="#4caf50"
                      d="M45,16.2l-5,2.75l-5,4.75L35,40h7c1.657,0,3-1.343,3-3V16.2z"
                    ></path>
                    <path
                      fill="#1e88e5"
                      d="M3,16.2l3.614,1.71L13,23.7V40H6c-1.657,0-3-1.343-3-3V16.2z"
                    ></path>
                    <polygon
                      fill="#e53935"
                      points="35,11.2 24,19.45 13,11.2 12,17 13,23.7 24,31.95 35,23.7 36,17"
                    ></polygon>
                    <path
                      fill="#c62828"
                      d="M3,12.298V16.2l10,7.5V11.2L9.876,8.859C9.132,8.301,8.228,8,7.298,8h0C4.924,8,3,9.924,3,12.298z"
                    ></path>
                    <path
                      fill="#fbc02d"
                      d="M45,12.298V16.2l-10,7.5V11.2l3.124-2.341C38.868,8.301,39.772,8,40.702,8h0 C43.076,8,45,9.924,45,12.298z"
                    ></path>
                  </svg>
                  {/* <FaEnvelope className="w-4 h-4 text-gray-400" /> */}
                  <span className="text-gray-400">Gmail</span>
                  <span className="ml-auto text-[10px] font-medium px-2 py-0.5 rounded-full bg-gray-700 text-gray-300">
                    Inactive
                  </span>
                </SidebarMenuButton>
              </SidebarMenuItem>

              <SidebarMenuItem className="mb-2">
                <SidebarMenuButton>
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    x="0px"
                    y="0px"
                    width="100"
                    height="100"
                    viewBox="0 0 48 48"
                  >
                    <rect
                      width="22"
                      height="22"
                      x="13"
                      y="13"
                      fill="#fff"
                    ></rect>
                    <polygon
                      fill="#1e88e5"
                      points="25.68,20.92 26.688,22.36 28.272,21.208 28.272,29.56 30,29.56 30,18.616 28.56,18.616"
                    ></polygon>
                    <path
                      fill="#1e88e5"
                      d="M22.943,23.745c0.625-0.574,1.013-1.37,1.013-2.249c0-1.747-1.533-3.168-3.417-3.168 c-1.602,0-2.972,1.009-3.33,2.453l1.657,0.421c0.165-0.664,0.868-1.146,1.673-1.146c0.942,0,1.709,0.646,1.709,1.44 c0,0.794-0.767,1.44-1.709,1.44h-0.997v1.728h0.997c1.081,0,1.993,0.751,1.993,1.64c0,0.904-0.866,1.64-1.931,1.64 c-0.962,0-1.784-0.61-1.914-1.418L17,26.802c0.262,1.636,1.81,2.87,3.6,2.87c2.007,0,3.64-1.511,3.64-3.368 C24.24,25.281,23.736,24.363,22.943,23.745z"
                    ></path>
                    <polygon
                      fill="#fbc02d"
                      points="34,42 14,42 13,38 14,34 34,34 35,38"
                    ></polygon>
                    <polygon
                      fill="#4caf50"
                      points="38,35 42,34 42,14 38,13 34,14 34,34"
                    ></polygon>
                    <path
                      fill="#1e88e5"
                      d="M34,14l1-4l-1-4H9C7.343,6,6,7.343,6,9v25l4,1l4-1V14H34z"
                    ></path>
                    <polygon
                      fill="#e53935"
                      points="34,34 34,42 42,34"
                    ></polygon>
                    <path
                      fill="#1565c0"
                      d="M39,6h-5v8h8V9C42,7.343,40.657,6,39,6z"
                    ></path>
                    <path
                      fill="#1565c0"
                      d="M9,42h5v-8H6v5C6,40.657,7.343,42,9,42z"
                    ></path>
                  </svg>
                  {/* <FaCalendar className="w-4 h-4 text-gray-400" /> */}
                  <span className="text-gray-400">Google Calendar</span>
                  <span className="ml-auto text-[10px] font-medium px-2 py-0.5 rounded-full bg-green-500 text-black">
                    Active
                  </span>
                </SidebarMenuButton>
              </SidebarMenuItem>

              <SidebarMenuItem className="mb-2">
                <SidebarMenuButton
                  onClick={async () => {
                    try {
                      await linkTwitter();
                    } catch (e) {
                      alert(
                        "Failed to connect Twitter: " + (e as Error).message
                      );
                    }
                  }}
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    x="0px"
                    y="0px"
                    width="18"
                    height="18"
                    viewBox="0 0 50 50"
                    fill="currentColor"
                    className="text-gray-400"
                  >
                    <path d="M 5.9199219 6 L 20.582031 27.375 L 6.2304688 44 L 9.4101562 44 L 21.986328 29.421875 L 31.986328 44 L 44 44 L 28.681641 21.669922 L 42.199219 6 L 39.029297 6 L 27.275391 19.617188 L 17.933594 6 L 5.9199219 6 z M 9.7167969 8 L 16.880859 8 L 40.203125 42 L 33.039062 42 L 9.7167969 8 z"></path>
                  </svg>
                  <span className="text-gray-400">X (Twitter)</span>
                  {isTwitterConnected ? (
                    <span className="ml-auto text-[10px] font-medium px-3 py-1 rounded-md bg-green-500 text-white cursor-pointer">
                      Connected
                    </span>
                  ) : (
                    <span className="ml-auto text-[10px] font-medium px-3 py-1 rounded-md bg-sky-500 hover:bg-sky-600 text-white cursor-pointer">
                      Connect
                    </span>
                  )}
                </SidebarMenuButton>
              </SidebarMenuItem>

              <SidebarMenuItem className="mb-2">
                <SidebarMenuButton>
                  <FaGoogleDrive className="w-4 h-4 text-gray-400" />
                  <span className="text-gray-400">Google Drive</span>
                  <span className="ml-auto text-[10px] font-medium px-2 py-0.5 rounded-full bg-gray-700 text-gray-300">
                    Inactive
                  </span>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroup>
        </SidebarContent>

        <SidebarFooter className="border-t border-gray-800 rounded-md">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <div className="flex items-center rounded-lg gap-3 p-4 cursor-pointer hover:bg-gray-800/50">
                <img
                  src={user?.user_metadata?.avatar_url || `https://ui-avatars.com/api/?name=${user?.user_metadata?.full_name}&background=4F46E5&color=fff`}
                  alt={user?.user_metadata?.full_name}
                  className="w-8 h-8 rounded-full"
                />
                <div className="flex-1">
                  <div className="text-sm text-gray-400 font-medium">
                    {user?.user_metadata?.full_name}
                  </div>
                </div>
                <ChevronsUpDown className="w-4 h-4 text-gray-400" />
              </div>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-56" align="end" side="top">
              {/* <DropdownMenuLabel>My Account</DropdownMenuLabel>
              <DropdownMenuSeparator /> */}
              {/* <DropdownMenuItem>Profile</DropdownMenuItem>
              <DropdownMenuItem>Settings</DropdownMenuItem>
              <DropdownMenuSeparator /> */}
              <DropdownMenuItem
                onClick={signOut}
                className="cursor-pointer text-red-500"
              >
                Log out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </SidebarFooter>
      </Sidebar>
    </SidebarProvider>
  );
};

export default ChatSidebar;
