"use client";

import { useState, useEffect, useRef } from 'react';
import { Send, Download, User, Bot, Scale, Upload as UploadIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useAuth } from '@/hooks/useAuth';
import AuthForm from '@/components/auth/AuthForm';
import UserMenu from '@/components/auth/UserMenu';
import SearchScopeSelector from '@/components/SearchScopeSelector';
import { useLocalStorage } from '@/hooks/useLocalStorage';
import ConversationTabs from '@/components/ConversationTabs';
import { api } from '@/lib/api';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
  sources?: Source[];
}

interface Source {
  document: string;
  page: number;
  relevance: number;
  excerpt: string;
}


interface Conversation {
  id: string;
  title: string;
  createdAt: Date;
  updatedAt: Date;
  messageCount: number;
  searchScope: 'precedents' | 'statutes' | 'both';
  messages: Message[];
}

export default function LegalRAGAssistant() {
  const { user, loading: authLoading } = useAuth();
  
  // State management
  const [conversations, setConversations] = useLocalStorage<Conversation[]>('legal-conversations', []);
  const [activeConversationId, setActiveConversationId] = useState<string>('');
  const [inputValues, setInputValues] = useState<Record<string, string>>({});
  const [loadingStates, setLoadingStates] = useState<Record<string, boolean>>({});
  const [searchScope, setSearchScope] = useState<'precedents' | 'statutes' | 'both'>('both');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Helper functions
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const generateConversationTitle = (firstMessage: string) => {
    return firstMessage.length > 30 ? firstMessage.substring(0, 30) + '...' : firstMessage;
  };

  // Effects
  useEffect(() => {
    scrollToBottom();
  }, [conversations]);

  // Debug logging to see what's happening with conversations
  useEffect(() => {
    console.log('Active conversation ID:', activeConversationId);
    console.log('Active conversation messages:', conversations.find(c => c.id === activeConversationId)?.messages?.length || 0);
    console.log('All conversations:', conversations.map(c => ({ id: c.id, messageCount: c.messages.length })));
  }, [activeConversationId, conversations]);

  // Initialize with mock data and first conversation
  useEffect(() => {
    if (user && conversations.length === 0) {
      const initialConversation: Conversation = {
        id: 'conv-1',
        title: 'Welcome Chat',
        createdAt: new Date(),
        updatedAt: new Date(),
        messageCount: 1,
        searchScope: 'both',
        messages: [
          {
            id: '1',
            content: 'Hello! I\'m your legal research assistant. I can help you analyze legal documents, search through precedents and statutes, and answer questions about corporate law, contracts, and more. Please select your search scope and start asking questions!',
            sender: 'assistant',
            timestamp: new Date()
          }
        ]
      };

      setConversations([initialConversation]);
      setActiveConversationId('conv-1');
    } else if (user && conversations.length > 0 && !activeConversationId) {
      // Set active conversation if we have conversations but no active one
      setActiveConversationId(conversations[0].id);
    }
  }, [user, conversations.length, activeConversationId, setConversations]);

  // Auth loading and user check
  if (authLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
        <div className="flex items-center gap-3">
          <Scale className="w-8 h-8 text-amber-600 animate-spin" />
          <span className="text-lg text-slate-600">Loading...</span>
        </div>
      </div>
    );
  }

  if (!user) {
    return <AuthForm />;
  }

  // Get active conversation
  const activeConversation = conversations.find(conv => conv.id === activeConversationId);
  const messages = activeConversation?.messages || [];
  const inputValue = inputValues[activeConversationId] || '';
  const isLoading = loadingStates[activeConversationId] || false;

const handleSendMessage = async () => {
  const currentInput = inputValues[activeConversationId] || '';
  if (!currentInput.trim() || !activeConversation) return;

  const userMessage: Message = {
    id: Date.now().toString(),
    content: currentInput,
    sender: 'user',
    timestamp: new Date()
  };

  const currentQuery = currentInput;

  setInputValues(prev => ({
    ...prev,
    [activeConversationId]: ''
  }));

  setLoadingStates(prev => ({ ...prev, [activeConversationId]: true }));

  try {
    const response = await api.sendMessage(
      currentQuery,
      searchScope === 'both' ? 'statutes' : searchScope
    );

    const assistantMessage: Message = {
      id: (Date.now() + 1).toString(),
      content: response.answer || response.response || 'No response received',
      sender: 'assistant',
      timestamp: new Date(),
      sources: response.sources || []
    };

    setConversations(prev => prev.map(conv => {
      if (conv.id !== activeConversationId) return conv;

      const updatedMessages = [...conv.messages, userMessage, assistantMessage];

      return {
        ...conv,
        messages: updatedMessages,
        messageCount: updatedMessages.length,
        updatedAt: new Date(),
        title: conv.messages.length === 1 ? generateConversationTitle(currentQuery) : conv.title
      };
    }));
  } catch (error) {
    const errorDetails = error instanceof Error ? error.message : 'Unknown error occurred';
    const isNetworkError = errorDetails.includes('fetch') || errorDetails.includes('Failed to fetch');

    const errorMessage: Message = {
      id: (Date.now() + 1).toString(),
      content: isNetworkError
        ? 'Connection error: Unable to reach the backend server. Please ensure your FastAPI server is running on the correct port and try again.'
        : `Error processing your request: ${errorDetails}. Please try again.`,
      sender: 'assistant',
      timestamp: new Date()
    };

    setConversations(prev => prev.map(conv => {
      if (conv.id !== activeConversationId) return conv;

      const updatedMessages = [...conv.messages, userMessage, errorMessage];

      return {
        ...conv,
        messages: updatedMessages,
        messageCount: updatedMessages.length,
        updatedAt: new Date()
      };
    }));
  } finally {
    setLoadingStates(prev => ({ ...prev, [activeConversationId]: false }));
  }
};


  const handleNewConversation = () => {
    const newConversation: Conversation = {
      id: `conv-${Date.now()}`,
      title: 'New Chat',
      createdAt: new Date(),
      updatedAt: new Date(),
      messageCount: 1,
      searchScope: searchScope,
      messages: [
        {
          id: Date.now().toString(),
          content: `Hello! I'm ready to help you with legal research. I'll search through ${searchScope === 'both' ? 'both precedents and statutes' : searchScope} based on your current selection. What would you like to know?`,
          sender: 'assistant',
          timestamp: new Date()
        }
      ]
    };

    setConversations(prev => [...prev, newConversation]);
    setActiveConversationId(newConversation.id);
    // Initialize empty input for new conversation
    setInputValues(prev => ({
      ...prev,
      [newConversation.id]: ''
    }));
  };

  const handleCloseConversation = (conversationId: string) => {
    setConversations(prev => {
      const filtered = prev.filter(conv => conv.id !== conversationId);
      if (activeConversationId === conversationId && filtered.length > 0) {
        setActiveConversationId(filtered[0].id);
      }
      return filtered;
    });
    // Clean up loading state for closed conversation
    setLoadingStates(prev => {
      const newStates = { ...prev };
      delete newStates[conversationId];
      return newStates;
    });
    // Clean up input value for closed conversation
    setInputValues(prev => {
      const newValues = { ...prev };
      delete newValues[conversationId];
      return newValues;
    });
  };

  const handleConversationChange = (conversationId: string) => {
    setActiveConversationId(conversationId);
  };

  const handleScopeChange = (scope: 'precedents' | 'statutes' | 'both') => {
    setSearchScope(scope);
    // Update active conversation's search scope
    if (activeConversation) {
      setConversations(prev => prev.map(conv => 
        conv.id === activeConversationId 
          ? { ...conv, searchScope: scope }
          : conv
      ));
    }
  };

  const exportConversation = () => {
    if (!activeConversation) return;
    
    const conversation = activeConversation.messages
      .map(msg => `${msg.sender.toUpperCase()}: ${msg.content}`)
      .join('\n\n');
    
    const blob = new Blob([conversation], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `legal-consultation-${activeConversation.title}-${new Date().toISOString().split('T')[0]}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Mock counts for now since we removed document management
  const precedentCount = 5;
  const statuteCount = 8;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="container mx-auto h-screen flex flex-col">
        {/* Header */}
        <div className="bg-white border-b border-slate-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-amber-600 rounded-lg flex items-center justify-center">
                <Scale className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-slate-800">LegalAI Assistant</h1>
                <p className="text-xs text-slate-600">Welcome, {user.email}</p>
              </div>
            </div>
            <UserMenu />
          </div>
        </div>

        {/* Conversation Tabs */}
        <ConversationTabs
          conversations={conversations}
          activeConversationId={activeConversationId}
          onConversationChange={handleConversationChange}
          onNewConversation={handleNewConversation}
          onCloseConversation={handleCloseConversation}
        />

        <div className="flex-1 flex">
          {/* Sidebar */}
          <div className="w-80 bg-white border-r border-slate-200 flex flex-col">
            <div className="flex-1 flex flex-col p-4 space-y-4 overflow-hidden">
              <SearchScopeSelector
                selectedScope={searchScope}
                onScopeChange={handleScopeChange}
                precedentCount={precedentCount}
                statuteCount={statuteCount}
              />

              <div className="flex-1">
                <h3 className="text-sm font-semibold text-slate-700 mb-3">Knowledge Base Summary</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center justify-between p-2 bg-amber-50 rounded">
                    <span className="text-amber-800">Legal Precedents</span>
                    <Badge variant="secondary">{precedentCount}</Badge>
                  </div>
                  <div className="flex items-center justify-between p-2 bg-blue-50 rounded">
                    <span className="text-blue-800">Statutes & Regulations</span>
                    <Badge variant="secondary">{statuteCount}</Badge>
                  </div>
                </div>
              </div>

              <Button
                onClick={exportConversation}
                variant="outline"
                className="w-full"
                size="sm"
                disabled={!activeConversation || activeConversation.messages.length <= 1}
              >
                <Download className="w-4 h-4 mr-2" />
                Export Chat
              </Button>
            </div>
          </div>

          {/* Main Chat Area */}
          <div className="flex-1 flex flex-col">
            {/* Chat Messages */}
            <ScrollArea className="flex-1 p-6">
              <div className="max-w-4xl mx-auto space-y-6">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex gap-4 ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`flex gap-3 max-w-3xl ${message.sender === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                        message.sender === 'user' 
                          ? 'bg-slate-800 text-white' 
                          : 'bg-amber-100 text-amber-800'
                      }`}>
                        {message.sender === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                      </div>
                      
                      <div className="flex-1">
                        <Card className={`${
                          message.sender === 'user' 
                            ? 'bg-slate-800 text-white' 
                            : 'bg-white border-slate-200'
                        }`}>
                          <CardContent className="p-4">
                            <div className="text-sm leading-relaxed whitespace-pre-wrap break-words">
                              {message.content}
                            </div>
                            
                            {message.sources && message.sources.length > 0 && (
                              <div className={`mt-4 pt-4 border-t ${message.sender === 'user' ? 'border-slate-600' : 'border-slate-200'}`}>
                                <h4 className={`text-xs font-semibold mb-2 ${message.sender === 'user' ? 'text-slate-300' : 'text-slate-600'}`}>Sources:</h4>
                                <div className="space-y-2">
                                  {message.sources.map((source, index) => (
                                    <div key={index} className={`p-2 rounded text-xs ${message.sender === 'user' ? 'bg-slate-700' : 'bg-slate-50'}`}>
                                      <div className="flex items-center justify-between mb-1">
                                        <span className={`font-medium ${message.sender === 'user' ? 'text-slate-200' : 'text-slate-800'}`}>{source.document}</span>
                                        <Badge variant="secondary" className="text-xs">
                                          Page {source.page}
                                        </Badge>
                                      </div>
                                      <p className={`italic ${message.sender === 'user' ? 'text-slate-300' : 'text-slate-600'}`}>"{source.excerpt}"</p>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                          </CardContent>
                        </Card>
                        
                        <p className="text-xs text-slate-500 mt-1 px-2">
                          {new Date(message.timestamp).toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
                
                {isLoading && (
                  <div className="flex gap-4 justify-start">
                    <div className="flex gap-3 max-w-3xl">
                      <div className="w-8 h-8 rounded-full bg-amber-100 text-amber-800 flex items-center justify-center">
                        <Bot className="w-4 h-4" />
                      </div>
                      <Card className="bg-white border-slate-200">
                        <CardContent className="p-4">
                          <div className="flex items-center gap-2">
                            <div className="w-2 h-2 bg-amber-600 rounded-full animate-bounce"></div>
                            <div className="w-2 h-2 bg-amber-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                            <div className="w-2 h-2 bg-amber-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                            <span className="text-sm text-slate-600 ml-2">
                              Analyzing your query... This may take 2-3 minutes for complex legal research.
                            </span>
                          </div>
                        </CardContent>
                      </Card>
                    </div>
                  </div>
                )}
                
                <div ref={messagesEndRef} />
              </div>
            </ScrollArea>

            {/* Input Area */}
            <div className="border-t border-slate-200 bg-white p-6">
              <div className="max-w-4xl mx-auto">
                <div className="flex gap-4">
                  <div className="flex-1">
                    <Input
                      value={inputValue}
                      onChange={(e) => setInputValues(prev => ({
                        ...prev,
                        [activeConversationId]: e.target.value
                      }))}
                      placeholder={`Ask your legal question... (Response may take 2-3 minutes)`}
                      onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSendMessage()}
                      className="h-12 border-slate-300 focus:border-amber-500 focus:ring-amber-500"
                    />
                  </div>
                  <Button
                    onClick={handleSendMessage}
                    disabled={!inputValue.trim() || isLoading}
                    className="h-12 px-6 bg-slate-800 hover:bg-slate-900 text-white"
                  >
                    {isLoading ? <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" /> : <Send className="w-4 h-4" />}
                  </Button>
                </div>
                
                <div className="flex items-center justify-between mt-3 text-xs text-slate-500">
                  <span>Press Enter to send • Backend response may take 2-3 minutes</span>
                  <span>
                    Searching: {searchScope === 'both' ? `${precedentCount + statuteCount} documents` : 
                    `${searchScope === 'precedents' ? precedentCount : statuteCount} ${searchScope}`}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}