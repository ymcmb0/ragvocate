import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'LegalAI Assistant - RAG-Powered Legal Research',
  description: 'AI-powered legal research assistant using TinyLlama and LangChain for document analysis and legal consultation.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  );
}