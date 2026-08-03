import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FilePlus, Plus, X, Sparkles } from 'lucide-react';
import { toast } from 'react-toastify';
import { QAPlanService } from '../api/services';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Textarea } from '../components/ui/Textarea';

export const CreatePlan: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  
  const [title, setTitle] = useState('');
  const [userStory, setUserStory] = useState('');
  const [implementationSummary, setImplementationSummary] = useState('');
  const [acList, setAcList] = useState<string[]>(['']);

  const handleAddAc = () => setAcList([...acList, '']);
  const handleRemoveAc = (index: number) => {
    if (acList.length > 1) {
      setAcList(acList.filter((_, i) => i !== index));
    }
  };
  const handleAcChange = (index: number, value: string) => {
    const newList = [...acList];
    newList[index] = value;
    setAcList(newList);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title || !userStory) {
      toast.error('Title and User Story are required.');
      return;
    }
    const filteredAc = acList.filter(a => a.trim() !== '');
    if (filteredAc.length === 0) {
      toast.error('At least one Acceptance Criterion is required.');
      return;
    }

    try {
      setLoading(true);
      const plan = await QAPlanService.createPlan({
        title,
        user_story: userStory,
        implementation_summary: implementationSummary,
        acceptance_criteria: filteredAc,
      });
      toast.success('Agentic QA Plan generated successfully!');
      navigate(`/plans/${plan.id}`);
    } catch (err) {
      toast.error('Failed to generate QA Plan.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-20">
      <div>
        <h1 className="text-3xl font-bold text-slate-100 flex items-center gap-2">
          <FilePlus className="h-8 w-8 text-purple-400" />
          Create QA Plan
        </h1>
        <p className="text-slate-400 mt-1">Let the AI agents analyze your requirements and generate comprehensive test cases.</p>
      </div>

      <Card>
        <form onSubmit={handleSubmit} className="space-y-6">
          <Input 
            label="Plan Title" 
            placeholder="e.g. Authentication Password Reset Flow" 
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            disabled={loading}
          />

          <Textarea 
            label="User Story / Requirement" 
            placeholder="As a [role], I want [feature] so that [benefit]..." 
            value={userStory}
            onChange={(e) => setUserStory(e.target.value)}
            required
            disabled={loading}
            rows={4}
          />

          <div className="space-y-3">
            <label className="text-sm font-medium text-slate-300">Acceptance Criteria</label>
            {acList.map((ac, index) => (
              <div key={index} className="flex gap-2">
                <Input 
                  placeholder={`AC${index + 1}: Expected behavior...`}
                  value={ac}
                  onChange={(e) => handleAcChange(index, e.target.value)}
                  disabled={loading}
                  className="flex-1"
                />
                <Button 
                  type="button" 
                  variant="outline" 
                  size="sm" 
                  onClick={() => handleRemoveAc(index)}
                  disabled={loading || acList.length === 1}
                  className="px-3"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            ))}
            <Button 
              type="button" 
              variant="ghost" 
              size="sm" 
              onClick={handleAddAc}
              disabled={loading}
              leftIcon={<Plus className="h-4 w-4" />}
            >
              Add Criterion
            </Button>
          </div>

          <Textarea 
            label="Implementation Summary (Optional)" 
            placeholder="Briefly describe the technical implementation or PR details for better context..." 
            value={implementationSummary}
            onChange={(e) => setImplementationSummary(e.target.value)}
            disabled={loading}
            rows={3}
          />

          <div className="pt-4 border-t border-slate-800 flex justify-end">
            <Button 
              type="submit" 
              isLoading={loading} 
              leftIcon={!loading && <Sparkles className="h-4 w-4 text-amber-300" />}
              className={loading ? 'w-full md:w-auto' : 'w-full md:w-auto bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500'}
            >
              {loading ? 'AI Agents are analyzing...' : 'Generate QA Plan'}
            </Button>
          </div>
        </form>
      </Card>
      
      {loading && (
        <div className="text-center text-sm text-slate-400 animate-pulse">
          This usually takes 10-30 seconds depending on complexity...
        </div>
      )}
    </div>
  );
};
