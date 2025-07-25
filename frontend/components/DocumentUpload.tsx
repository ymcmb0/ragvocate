"use client";

import { useState, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Upload, FileText, Trash2, CheckCircle, Clock, AlertCircle } from 'lucide-react';
import { Document } from '@/types/api';

interface DocumentUploadProps {
  documents: Document[];
  onUpload: (files: FileList, category: 'precedents' | 'statutes') => Promise<void>;
  onDelete: (documentId: string) => void;
}

export default function DocumentUpload({ documents, onUpload, onDelete }: DocumentUploadProps) {
  const [selectedCategory, setSelectedCategory] = useState<'precedents' | 'statutes'>('precedents');
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = async (files: FileList) => {
    if (files.length === 0) return;
    
    setUploading(true);
    try {
      await onUpload(files, selectedCategory);
    } catch (error) {
      console.error('Upload failed:', error);
    } finally {
      setUploading(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusIcon = (status: Document['status']) => {
    switch (status) {
      case 'ready':
        return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'processing':
        return <Clock className="w-4 h-4 text-amber-600 animate-spin" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-600" />;
    }
  };

  const precedentDocs = documents.filter(doc => doc.category === 'precedents');
  const statuteDocs = documents.filter(doc => doc.category === 'statutes');

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Upload className="w-5 h-5" />
            Upload Legal Documents
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label className="text-sm font-medium mb-3 block">Document Category</Label>
            <RadioGroup
              value={selectedCategory}
              onValueChange={(value) => setSelectedCategory(value as 'precedents' | 'statutes')}
              className="flex gap-6"
            >
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="precedents" id="precedents" />
                <Label htmlFor="precedents" className="cursor-pointer">
                  Legal Precedents
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="statutes" id="statutes" />
                <Label htmlFor="statutes" className="cursor-pointer">
                  Statutes & Regulations
                </Label>
              </div>
            </RadioGroup>
          </div>

          <Button
            onClick={() => fileInputRef.current?.click()}
            className="w-full bg-amber-600 hover:bg-amber-700 text-white"
            disabled={uploading}
          >
            <Upload className="w-4 h-4 mr-2" />
            {uploading ? 'Uploading...' : `Upload ${selectedCategory === 'precedents' ? 'Precedents' : 'Statutes'}`}
          </Button>
          
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf,.doc,.docx,.txt"
            className="hidden"
            onChange={(e) => e.target.files && handleFileUpload(e.target.files)}
          />
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Legal Precedents ({precedentDocs.length})</CardTitle>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-64">
              <div className="space-y-2">
                {precedentDocs.map((doc) => (
                  <div key={doc.id} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                    <div className="flex items-center gap-3 flex-1 min-w-0">
                      <FileText className="w-4 h-4 text-amber-600 flex-shrink-0" />
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-medium text-slate-800 truncate">{doc.name}</p>
                        <div className="flex items-center gap-2 mt-1">
                          {getStatusIcon(doc.status)}
                          <span className="text-xs text-slate-500">{formatFileSize(doc.size)}</span>
                        </div>
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onDelete(doc.id)}
                      className="text-red-500 hover:text-red-700 flex-shrink-0"
                    >
                      <Trash2 className="w-3 h-3" />
                    </Button>
                  </div>
                ))}
                {precedentDocs.length === 0 && (
                  <p className="text-sm text-slate-500 text-center py-8">No precedents uploaded yet</p>
                )}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Statutes & Regulations ({statuteDocs.length})</CardTitle>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-64">
              <div className="space-y-2">
                {statuteDocs.map((doc) => (
                  <div key={doc.id} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                    <div className="flex items-center gap-3 flex-1 min-w-0">
                      <FileText className="w-4 h-4 text-blue-600 flex-shrink-0" />
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-medium text-slate-800 truncate">{doc.name}</p>
                        <div className="flex items-center gap-2 mt-1">
                          {getStatusIcon(doc.status)}
                          <span className="text-xs text-slate-500">{formatFileSize(doc.size)}</span>
                        </div>
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onDelete(doc.id)}
                      className="text-red-500 hover:text-red-700 flex-shrink-0"
                    >
                      <Trash2 className="w-3 h-3" />
                    </Button>
                  </div>
                ))}
                {statuteDocs.length === 0 && (
                  <p className="text-sm text-slate-500 text-center py-8">No statutes uploaded yet</p>
                )}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}