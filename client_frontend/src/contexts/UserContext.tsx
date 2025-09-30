import React, { createContext, useContext, useState, ReactNode } from 'react';

export type UserRole = 'student' | 'teacher' | 'processor' | null;

interface User {
  role: UserRole;
  id: string;
  name: string;
}

interface UserContextType {
  user: User | null;
  setUser: (user: User | null) => void;
  login: (role: UserRole, id: string, name: string) => void;
  logout: () => void;
  isTeacher: boolean;
  isStudent: boolean;
  isProcessor: boolean;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export const UserProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(() => {
    // Try to load from localStorage
    const saved = localStorage.getItem('exam_user');
    return saved ? JSON.parse(saved) : null;
  });

  const login = (role: UserRole, id: string, name: string) => {
    const newUser = { role, id, name };
    setUser(newUser);
    localStorage.setItem('exam_user', JSON.stringify(newUser));
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('exam_user');
  };

  const value: UserContextType = {
    user,
    setUser,
    login,
    logout,
    isTeacher: user?.role === 'teacher',
    isStudent: user?.role === 'student',
    isProcessor: user?.role === 'processor',
  };

  return <UserContext.Provider value={value}>{children}</UserContext.Provider>;
};

export const useUser = () => {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
};
