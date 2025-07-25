"use client";

import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Scale, BookOpen, Search } from 'lucide-react';

interface SearchScopeSelectorProps {
  selectedScope: 'precedents' | 'statutes' | 'both';
  onScopeChange: (scope: 'precedents' | 'statutes' | 'both') => void;
  precedentCount: number;
  statuteCount: number;
}

export default function SearchScopeSelector({ 
  selectedScope, 
  onScopeChange, 
  precedentCount, 
  statuteCount 
}: SearchScopeSelectorProps) {
  return (
    <Card className="mb-4">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm flex items-center gap-2">
          <Search className="w-4 h-4" />
          Search Scope
        </CardTitle>
      </CardHeader>
      <CardContent>
        <RadioGroup
          value={selectedScope}
          onValueChange={(value) => onScopeChange(value as 'precedents' | 'statutes' | 'both')}
          className="space-y-3"
        >
          <div className="flex items-center space-x-3 p-2 rounded-lg hover:bg-slate-50">
            <RadioGroupItem value="precedents" id="search-precedents" />
            <Label htmlFor="search-precedents" className="cursor-pointer flex items-center gap-2 flex-1">
              <Scale className="w-4 h-4 text-amber-600" />
              <span>Legal Precedents</span>
              <span className="text-xs text-slate-500">({precedentCount} docs)</span>
            </Label>
          </div>
          
          <div className="flex items-center space-x-3 p-2 rounded-lg hover:bg-slate-50">
            <RadioGroupItem value="statutes" id="search-statutes" />
            <Label htmlFor="search-statutes" className="cursor-pointer flex items-center gap-2 flex-1">
              <BookOpen className="w-4 h-4 text-blue-600" />
              <span>Statutes & Regulations</span>
              <span className="text-xs text-slate-500">({statuteCount} docs)</span>
            </Label>
          </div>
          
          <div className="flex items-center space-x-3 p-2 rounded-lg hover:bg-slate-50">
            <RadioGroupItem value="both" id="search-both" />
            <Label htmlFor="search-both" className="cursor-pointer flex items-center gap-2 flex-1">
              <div className="flex items-center gap-1">
                <Scale className="w-3 h-3 text-amber-600" />
                <BookOpen className="w-3 h-3 text-blue-600" />
              </div>
              <span>Both Precedents & Statutes</span>
              <span className="text-xs text-slate-500">({precedentCount + statuteCount} docs)</span>
            </Label>
          </div>
        </RadioGroup>
      </CardContent>
    </Card>
  );
}