const KEY = "token";
export const getToken = (): string | null =>
  typeof window === "undefined" ? null : localStorage.getItem(KEY);
export const setToken = (t: string) => localStorage.setItem(KEY, t);
export const clearToken = () => localStorage.removeItem(KEY);