"use client";

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Plus, X, MessageSquare } from 'lucide-react';
import { Conversation } from '@/types/api';

interface ConversationTabsProps {
  conversations: Conversation[];
  activeConversationId: string;
  onConversationChange: (conversationId: string) => void;
  onNewConversation: () => void;
  onCloseConversation: (conversationId: string) => void;
}

export default function ConversationTabs({
  conversations,
  activeConversationId,
  onConversationChange,
  onNewConversation,
  onCloseConversation
}: ConversationTabsProps) {
  const truncateTitle = (title: string, maxLength: number = 20) => {
    return title.length > maxLength ? title.substring(0, maxLength) + '...' : title;
  };

  return (
    <div className="border-b border-slate-200 bg-white">
      <div className="flex items-center">
        <ScrollArea className="flex-1">
          <div className="flex items-center">
            {conversations.map((conversation) => (
              <div
                key={conversation.id}
                className={`flex items-center border-r border-slate-200 ${
                  activeConversationId === conversation.id
                    ? 'bg-slate-100 border-b-2 border-b-amber-600'
                    : 'hover:bg-slate-50'
                }`}
              >
                <button
                  onClick={() => onConversationChange(conversation.id)}
                  className="flex items-center gap-2 px-4 py-3 text-sm font-medium text-slate-700 hover:text-slate-900 min-w-0"
                >
                  <MessageSquare className="w-4 h-4 flex-shrink-0" />
                  <span className="truncate max-w-32">
                    {truncateTitle(conversation.title)}
                  </span>
                  <span className="text-xs text-slate-500 bg-slate-200 px-1.5 py-0.5 rounded-full">
                    {conversation.messageCount}
                  </span>
                </button>
                
                {conversations.length > 1 && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      onCloseConversation(conversation.id);
                    }}
                    className="h-8 w-8 p-0 text-slate-400 hover:text-slate-600 mr-2"
                  >
                    <X className="w-3 h-3" />
                  </Button>
                )}
              </div>
            ))}
          </div>
        </ScrollArea>
        
        <Button
          onClick={onNewConversation}
          variant="ghost"
          size="sm"
          className="flex-shrink-0 mx-2 text-slate-600 hover:text-slate-800"
        >
          <Plus className="w-4 h-4 mr-1" />
          New Chat
        </Button>
      </div>
    </div>
  );
}