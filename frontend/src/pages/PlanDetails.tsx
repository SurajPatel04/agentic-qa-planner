import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Camera, History, Target, FlaskConical, LayoutDashboard, TerminalSquare, Check, X } from 'lucide-react';
import { toast } from 'react-toastify';
import { QAPlanService } from '../api/services';
import type { QAPlanDetailResponse, TestCase } from '../api/types';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { TestCaseEditor } from '../components/TestCaseEditor';

type TabType = 'overview' | 'tests' | 'versions';

export const PlanDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [plan, setPlan] = useState<QAPlanDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<TabType>('overview');

  const fetchPlan = async () => {
    if (!id) return;
    try {
      setLoading(true);
      const data = await QAPlanService.getPlan(id);
      setPlan(data);
    } catch (err) {
      toast.error('Failed to load plan details');
      navigate('/');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPlan();
  }, [id]);

  const handleCreateSnapshot = async () => {
    if (!id) return;
    const summary = window.prompt('Enter a brief summary of what changed in this version:');
    if (!summary) return;

    try {
      await QAPlanService.createVersion(id, { change_summary: summary });
      toast.success('Version snapshot created successfully');
      fetchPlan();
    } catch (err) {
      toast.error('Failed to create version');
    }
  };

  const handleUpdateTestCase = (updated: TestCase) => {
    if (!plan) return;
    setPlan({
      ...plan,
      test_cases: plan.test_cases.map(t => t.id === updated.id ? updated : t)
    });
  };

  const handleUpdatePlanStatus = async (status: string) => {
    if (!plan) return;
    try {
      setLoading(true);
      await QAPlanService.updatePlan(plan.id, { status });
      toast.success(`Plan marked as ${status}`);
      fetchPlan();
    } catch (err) {
      toast.error('Failed to update plan status');
    } finally {
      setLoading(false);
    }
  };

  if (loading || !plan) {
    return (
      <div className="flex justify-center items-center h-full pt-20">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  const coverage = plan.coverage_summary?.coverage_percentage || 0;

  return (
    <div className="max-w-6xl mx-auto pb-20">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-3">
            <Badge variant="purple">v{plan.current_version}</Badge>
            <Badge variant={plan.status === 'APPROVED' ? 'success' : plan.status === 'REJECTED' ? 'error' : 'default'} className="uppercase">
              {plan.status}
            </Badge>
          </div>
          <div className="flex gap-2">
            <Button 
              size="sm" 
              variant="ghost" 
              className={`text-emerald-400 hover:text-emerald-300 hover:bg-emerald-500/10 ${plan.status.toUpperCase() === 'APPROVED' ? 'opacity-30 cursor-not-allowed text-emerald-900/50' : ''}`}
              onClick={() => handleUpdatePlanStatus('APPROVED')} 
              disabled={loading || plan.status.toUpperCase() === 'APPROVED'}
            >
              <Check className="h-4 w-4 mr-1" /> Approve Plan
            </Button>
            <Button 
              size="sm" 
              variant="ghost" 
              className={`text-red-400 hover:text-red-300 hover:bg-red-500/10 ${plan.status.toUpperCase() === 'REJECTED' ? 'opacity-30 cursor-not-allowed text-red-900/50' : ''}`}
              onClick={() => handleUpdatePlanStatus('REJECTED')} 
              disabled={loading || plan.status.toUpperCase() === 'REJECTED'}
            >
              <X className="h-4 w-4 mr-1" /> Reject Plan
            </Button>
          </div>
        </div>
        <h1 className="text-3xl font-bold text-slate-100 mb-2">{plan.title}</h1>
        <p className="text-slate-400">Generated {new Date(plan.created_at).toLocaleString()}</p>
      </div>

      {/* Tabs */}
      <div className="flex space-x-1 bg-slate-900/50 p-1 rounded-xl border border-slate-800/50 mb-6 inline-flex">
        <button
          onClick={() => setActiveTab('overview')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
            activeTab === 'overview' ? 'bg-indigo-500/20 text-indigo-400' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
          }`}
        >
          <LayoutDashboard className="h-4 w-4" /> Overview
        </button>
        <button
          onClick={() => setActiveTab('tests')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
            activeTab === 'tests' ? 'bg-indigo-500/20 text-indigo-400' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
          }`}
        >
          <FlaskConical className="h-4 w-4" /> Test Cases ({plan.test_cases.length})
        </button>
        <button
          onClick={() => setActiveTab('versions')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
            activeTab === 'versions' ? 'bg-indigo-500/20 text-indigo-400' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
          }`}
        >
          <History className="h-4 w-4" /> Versions
        </button>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="md:col-span-2">
              <h2 className="text-xl font-semibold mb-4 text-slate-200 flex items-center gap-2">
                <Target className="h-5 w-5 text-indigo-400" />
                Requirement
              </h2>
              <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-800/50 text-slate-300 font-mono text-sm mb-6 whitespace-pre-wrap">
                {plan.requirement_or_user_story}
              </div>
              
              <h3 className="font-semibold text-slate-200 mb-3">Acceptance Criteria</h3>
              <ul className="space-y-3">
                {(plan.acceptance_criteria || []).map(ac => (
                  <li key={ac.id} className="flex gap-3 text-slate-300 text-sm p-3 bg-slate-900/30 rounded-lg border border-slate-800/30">
                    <Badge variant="default">{ac.identifier}</Badge>
                    <span>{ac.text}</span>
                  </li>
                ))}
              </ul>
            </Card>

            <div className="space-y-6">
              <Card>
                <h2 className="font-semibold text-slate-200 mb-4">Coverage Score</h2>
                <div className="flex items-center justify-center py-6">
                  <div className="relative h-32 w-32 flex items-center justify-center rounded-full border-8 border-slate-800">
                    <div 
                      className={`absolute inset-0 rounded-full border-8 ${
                        coverage === 100 ? 'border-emerald-500' : coverage > 70 ? 'border-amber-500' : 'border-red-500'
                      }`}
                      style={{ 
                        clipPath: `polygon(0 0, 100% 0, 100% ${coverage}%, 0 ${coverage}%)`,
                        transform: 'rotate(-90deg)'
                      }}
                    />
                    <span className="text-3xl font-bold text-slate-100">{Math.round(coverage)}%</span>
                  </div>
                </div>
                <div className="text-center text-sm text-slate-400 mt-2">
                  {plan.coverage_summary?.covered_criteria_count || 0} of {plan.coverage_summary?.total_criteria_count || 0} ACs covered
                </div>
                {(plan.coverage_summary?.uncovered_criteria || []).length > 0 && (
                  <div className="mt-4 pt-4 border-t border-slate-800">
                    <p className="text-sm font-medium text-red-400 mb-2">Uncovered ACs:</p>
                    <div className="flex flex-wrap gap-1">
                      {(plan.coverage_summary?.uncovered_criteria || []).map((ac: string) => (
                        <Badge key={ac} variant="error">{ac}</Badge>
                      ))}
                    </div>
                  </div>
                )}
              </Card>

              {(plan.assumptions || []).length > 0 && (
                <Card>
                  <h2 className="font-semibold text-slate-200 mb-3">AI Assumptions</h2>
                  <ul className="list-disc list-inside text-sm text-slate-400 space-y-2">
                    {(plan.assumptions || []).map((a, i) => <li key={i}>{a}</li>)}
                  </ul>
                </Card>
              )}
            </div>
          </div>

          <Card>
            <h2 className="text-xl font-semibold mb-4 text-slate-200 flex items-center gap-2">
              <TerminalSquare className="h-5 w-5 text-slate-400" />
              Graph Execution Log
            </h2>
            <div className="space-y-3">
              {(plan.execution_logs || []).map(log => (
                <div key={log.id} className="flex gap-4 items-start p-3 bg-slate-900/50 rounded-lg border border-slate-800/50">
                  <Badge variant={log.status.toLowerCase().includes('success') ? 'success' : 'warning'} className="mt-0.5 whitespace-nowrap">
                    {log.node}
                  </Badge>
                  <div className="text-sm text-slate-300">
                    <p>{log.message}</p>
                    {log.details && log.details.sources && log.details.sources.length > 0 && (
                      <p className="text-slate-500 text-xs mt-1">Sources: {log.details.sources.join(', ')}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}

      {/* Test Cases Tab */}
      {activeTab === 'tests' && (
        <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
          {(plan.test_cases || []).map(tc => (
            <TestCaseEditor key={tc.id} testCase={tc} onUpdate={handleUpdateTestCase} />
          ))}
        </div>
      )}

      {/* Versions Tab */}
      {activeTab === 'versions' && (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
          <div className="flex justify-end">
            <Button onClick={handleCreateSnapshot} leftIcon={<Camera className="h-4 w-4" />}>
              Create Snapshot
            </Button>
          </div>
          
          <div className="relative border-l-2 border-indigo-500/20 ml-4 space-y-8 pb-8">
            {(plan.versions || []).map(v => (
              <div key={v.id} className="relative pl-8">
                <div className="absolute -left-[9px] top-1 h-4 w-4 rounded-full bg-slate-950 border-2 border-indigo-500" />
                <Card className="hover:border-indigo-500/30 transition-colors">
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex items-center gap-3">
                      <Badge variant="purple" className="text-sm">v{v.version_number}</Badge>
                      <h3 className="font-semibold text-slate-200">{v.change_summary}</h3>
                    </div>
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      onClick={() => navigate(`/plans/${plan.id}/versions/${v.version_number}`)}
                    >
                      View Details
                    </Button>
                  </div>
                  <p className="text-sm text-slate-500">Captured {new Date(v.created_at).toLocaleString()}</p>
                </Card>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
