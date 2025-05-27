import React, { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import CustomLoginForm from './CustomLoginForm';
import CustomRegisterForm from './CustomRegisterForm';
import { useAuth } from '@/context/AuthContext';

const AuthModal = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState('login');
  const { loginAnonymously } = useAuth();

  const handleSuccess = () => {
    onClose();
  };

  const handleAnonymousAccess = async () => {
    try {
      await loginAnonymously();
      onClose();
    } catch (error) {
      console.error("Error with anonymous login:", error);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle className="text-center text-xl font-semibold">
            {activeTab === 'login' ? 'Welcome Back' : 'Create an Account'}
          </DialogTitle>
        </DialogHeader>
        
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-2 mb-4">
            <TabsTrigger value="login">Login</TabsTrigger>
            <TabsTrigger value="register">Register</TabsTrigger>
          </TabsList>
          
          <TabsContent value="login" className="space-y-4">
            <CustomLoginForm onSuccess={handleSuccess} />
          </TabsContent>
          
          <TabsContent value="register" className="space-y-4">
            <CustomRegisterForm onSuccess={handleSuccess} />
          </TabsContent>
        </Tabs>
        
        <DialogFooter className="flex flex-col">
          <div className="relative flex items-center py-2">
            <div className="flex-grow border-t border-muted"></div>
            <span className="mx-4 text-xs text-muted-foreground">OR</span>
            <div className="flex-grow border-t border-muted"></div>
          </div>
          
          <Button 
            variant="outline" 
            onClick={handleAnonymousAccess}
            className="w-full"
          >
            Continue Anonymously
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default AuthModal;