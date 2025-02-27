// frontend/src/components/chat/ChatInterface.js
import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useToast } from '@/components/ui/use-toast';
import { Loader2, Send, Plus, Search } from 'lucide-react';
import PatientHistory from './PatientHistory';

export default function ChatInterface() {
  const { sessionId } = useParams();
  const [session, setSession] = useState(null);
  const [patientInfo, setPatientInfo] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [sending, setSending] = useState(false);
  const [showPatientHistory, setShowPatientHistory] = useState(false);
  const messagesEndRef = useRef(null);
  const { toast } = useToast();

  // Fetch session and messages
  useEffect(() => {
    const fetchSession = async () => {
      try {
        const response = await axios.get(`/api/chat/session/${sessionId}`);
        setSession(response.data);
        setMessages(response.data.messages || []);
        
        // Fetch patient info
        const patientResponse = await axios.get(`/api/documents/patient/${response.data.patient_id}`);
        setPatientInfo(patientResponse.data);
      } catch (error) {
        console.error("Error fetching chat session:", error);
        toast({
          variant: "destructive",
          title: "Error Loading Chat",
          description: "Failed to load chat session. Please try again.",
        });
      }
    };
    
    fetchSession();
  }, [sessionId, toast]);
  
  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!newMessage.trim()) return;
    
    setSending(true);
    
    try {
      const response = await axios.post(`/api/chat/session/${sessionId}/message`, {
        content: newMessage
      });
      
      // Add both user and assistant messages
      if (response.data.user_message && response.data.assistant_message) {
        setMessages([...messages, response.data.user_message, response.data.assistant_message]);
      } else if (response.data.user_message) {
        setMessages([...messages, response.data.user_message]);
        // Show error message if we got user message but no assistant message
        if (response.data.error) {
          toast({
            variant: "destructive",
            title: "AI Response Error",
            description: "The assistant couldn't generate a response. Please try again.",
          });
        }
      }
      
      setNewMessage('');
    } catch (error) {
      console.error("Error sending message:", error);
      toast({
        variant: "destructive",
        title: "Failed to Send",
        description: "Your message couldn't be sent. Please try again.",
      });
    } finally {
      setSending(false);
    }
  };

  const togglePatientHistory = () => {
    setShowPatientHistory(!showPatientHistory);
  };

  if (!session) {
    return (
      <div className="flex justify-center items-center h-64">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 h-full">
      {/* Main Chat */}
      <Card className="md:col-span-2 flex flex-col h-[calc(100vh-200px)]">
        <CardHeader className="pb-2">
          <div className="flex justify-between items-center">
            <CardTitle>
              Medical Assistant
              {patientInfo && (
                <span className="text-sm font-normal ml-2 text-gray-500">
                  Patient: {patientInfo.documents[0]?.metadata?.patient_name || "Unknown"}
                </span>
              )}
            </CardTitle>
            <Button variant="outline" size="sm" onClick={togglePatientHistory}>
              <Search className="h-4 w-4 mr-2" />
              Patient History
            </Button>
          </div>
        </CardHeader>
        
        <CardContent className="flex-grow overflow-y-auto px-4 py-0">
          <div className="space-y-4">
            {messages.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <p>No messages yet. Ask a question about this patient's medical history.</p>
              </div>
            ) : (
              messages.map((msg, index) => (
                <div
                  key={index}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div 
                    className={`max-w-[80%] rounded-lg px-4 py-2 ${
                      msg.role === 'user' 
                        ? 'bg-blue-500 text-white' 
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                    <p className="text-xs opacity-70 mt-1">
                      {new Date(msg.timestamp).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))
            )}
            <div ref={messagesEndRef} />
          </div>
        </CardContent>
        
        <CardFooter className="p-4 border-t">
          <form onSubmit={handleSendMessage} className="flex w-full gap-2">
            <Input
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              placeholder="Ask about the patient's medical history..."
              disabled={sending}
              className="flex-grow"
            />
            <Button type="submit" disabled={sending || !newMessage.trim()}>
              {sending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </form>
        </CardFooter>
      </Card>
      
      {/* Patient History Panel */}
      {showPatientHistory && (
        <Card className="md:col-span-1 h-[calc(100vh-200px)] overflow-y-auto">
          <CardHeader>
            <CardTitle>Patient Documents</CardTitle>
          </CardHeader>
          <CardContent>
            {patientInfo ? (
              <PatientHistory patientInfo={patientInfo} />
            ) : (
              <div className="flex justify-center items-center h-32">
                <Loader2 className="h-6 w-6 animate-spin" />
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}