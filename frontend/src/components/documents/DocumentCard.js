import React from 'react';
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Eye, Download, AlertTriangle, FileText, FileCheck } from 'lucide-react';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';

const DocumentCard = ({ document, onClick }) => {
  const getDocumentTypeIcon = () => {
    const typeMap = {
      'lab_result': <FileText className="h-6 w-6 text-blue-500" />,
      'prescription': <FileText className="h-6 w-6 text-green-500" />,
      'clinical_note': <FileText className="h-6 w-6 text-amber-500" />,
      'radiology': <FileText className="h-6 w-6 text-purple-500" />,
      'discharge': <FileText className="h-6 w-6 text-red-500" />,
      'consent': <FileCheck className="h-6 w-6 text-gray-500" />,
      'referral': <FileText className="h-6 w-6 text-indigo-500" />
    };
    
    return typeMap[document.documentType] || <FileText className="h-6 w-6 text-gray-500" />;
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    });
  };

  const truncateText = (text, maxLength = 100) => {
    if (!text) return '';
    return text.length > maxLength ? `${text.substring(0, maxLength)}...` : text;
  };

  return (
    <Card className="h-full flex flex-col overflow-hidden hover:border-blue-300 transition-all duration-200">
      <CardHeader className="pb-2 pt-4 px-4 flex-row gap-3 items-center">
        {getDocumentTypeIcon()}
        <div className="flex-1 overflow-hidden">
          <h3 className="font-medium text-sm line-clamp-1" title={document.title}>
            {document.title}
          </h3>
          <p className="text-xs text-gray-500">
            {formatDate(document.uploadDate)}
          </p>
        </div>
        {document.complianceChecks && !document.complianceChecks.compliant && (
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger>
                <AlertTriangle className="h-5 w-5 text-amber-500" />
              </TooltipTrigger>
              <TooltipContent>
                <p>Potential compliance issues detected</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        )}
      </CardHeader>
      
      <CardContent className="px-4 py-2 flex-1">
        <div className="text-xs text-gray-600 line-clamp-3">
          {truncateText(document.summary || 'No summary available')}
        </div>
        
        <div className="mt-3 flex flex-wrap gap-1">
          {document.tags && document.tags.slice(0, 3).map((tag, index) => (
            <Badge key={index} variant="outline" className="text-xs font-normal">
              {tag}
            </Badge>
          ))}
          {document.tags && document.tags.length > 3 && (
            <Badge variant="outline" className="text-xs font-normal">
              +{document.tags.length - 3} more
            </Badge>
          )}
        </div>
      </CardContent>
      
      <CardFooter className="px-4 py-3 border-t bg-gray-50 gap-2">
        <Button 
          variant="outline" 
          size="sm" 
          className="h-8 text-xs w-full" 
          onClick={() => onClick(document)}
        >
          <Eye className="h-3 w-3 mr-1" />
          View
        </Button>
        <Button 
          variant="outline" 
          size="sm" 
          className="h-8 text-xs"
        >
          <Download className="h-3 w-3" />
        </Button>
      </CardFooter>
    </Card>
  );
};

export default DocumentCard;