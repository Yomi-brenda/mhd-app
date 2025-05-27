import React from 'react';
import { Button } from "@/components/ui/button";
import { Shield } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";
import { useAuth } from '@/context/AuthContext';

const AnonymousAccess = ({ onSuccess }) => {
  const { toast } = useToast();
  const { continueAnonymously } = useAuth();

  const handleAnonymousAccess = () => {
    continueAnonymously();
    toast({
      title: "Anonymous Access Granted",
      description: "You are now browsing anonymously.",
    });
    onSuccess();
  };

  return (
    <div className="space-y-4 py-4">
      <div className="bg-secondary/50 p-4 rounded-lg flex items-start space-x-3">
        <Shield className="text-primary mt-1" />
        <div>
          <h3 className="font-medium">Anonymous Access</h3>
          <p className="text-sm text-muted-foreground mt-1">
            Continue without creating an account. Your data will not be stored between sessions and some features may be limited.
          </p>
        </div>
      </div>
      
      <div className="space-y-2">
        <h4 className="text-sm font-medium">Benefits of anonymous access:</h4>
        <ul className="list-disc list-inside text-sm text-muted-foreground space-y-1">
          <li>No personal information required</li>
          <li>Access to essential mental health resources</li>
          <li>Use the Symptom Checker and AI Chatbot</li>
          <li>Browse the Resources section</li>
        </ul>
      </div>
      
      <div className="space-y-2">
        <h4 className="text-sm font-medium">Limitations:</h4>
        <ul className="list-disc list-inside text-sm text-muted-foreground space-y-1">
          <li>Cannot save your progress or assessment results</li>
          <li>Limited community features</li>
          <li>Cannot book sessions with psychologists</li>
          <li>Preferences and settings are not remembered</li>
        </ul>
      </div>
      
      <Button 
        onClick={handleAnonymousAccess} 
        className="w-full bg-secondary text-foreground hover:bg-secondary/80"
      >
        Continue Anonymously
      </Button>
    </div>
  );
};

export default AnonymousAccess;