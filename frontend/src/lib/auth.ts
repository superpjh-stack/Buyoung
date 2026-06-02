"use client";
import { create } from "zustand";
import { authApi } from "./api";

interface User {
  user_id: string;
  username: string;
  role: string;
  department: string;
}

interface AuthStore {
  user: User | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  fetchMe: () => Promise<void>;
}

export const useAuth = create<AuthStore>((set) => ({
  user: null,
  loading: false,

  login: async (username, password) => {
    set({ loading: true });
    try {
      // login endpoint returns { access_token, user, ... } directly (no ok() wrapper)
      const res = await authApi.login(username, password);
      localStorage.setItem("access_token", res.data.access_token);
      set({ user: res.data.user, loading: false });
    } catch (e) {
      set({ loading: false });
      throw e;
    }
  },

  logout: () => {
    localStorage.removeItem("access_token");
    set({ user: null });
    window.location.href = "/login";
  },

  fetchMe: async () => {
    try {
      // /me returns UserOut directly (no ok() wrapper)
      const res = await authApi.me();
      set({ user: res.data });
    } catch {
      set({ user: null });
    }
  },
}));
