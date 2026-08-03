import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, LayoutDashboard, Trash2 } from 'lucide-react';
import { toast } from 'react-toastify';
import { QAPlanService } from '../api/services';
import type { QAPlanResponse } from '../api/types';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [plans, setPlans] = useState<QAPlanResponse[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchPlans = async () => {
    try {
      setLoading(true);
      const data = await QAPlanService.listPlans();
      setPlans(data);
    } catch (err) {
      toast.error('Failed to load QA Plans.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPlans();
  }, []);

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this plan?')) return;
    
    try {
      await QAPlanService.deletePlan(id);
      toast.success('Plan deleted successfully');
      fetchPlans();
    } catch (err) {
      toast.error('Failed to delete plan.');
    }
  };

  const getStatusVariant = (status: string) => {
    switch(status.toLowerCase()) {
      case 'approved': return 'success';
      case 'reviewed': return 'info';
      case 'archived': return 'default';
      default: return 'warning';
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-100 flex items-center gap-2">
            <LayoutDashboard className="h-8 w-8 text-indigo-400" />
            QA Plans
          </h1>
          <p className="text-slate-400 mt-1">Manage and track your AI-generated QA plans.</p>
        </div>
        <Button onClick={() => navigate('/plans/new')} leftIcon={<Plus className="h-4 w-4" />}>
          New Plan
        </Button>
      </div>

      {loading ? (
        <div className="flex justify-center py-20">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
        </div>
      ) : plans.length === 0 ? (
        <Card className="text-center py-16 flex flex-col items-center">
          <div className="w-16 h-16 bg-slate-800/50 rounded-full flex items-center justify-center mb-4">
            <LayoutDashboard className="h-8 w-8 text-slate-500" />
          </div>
          <h3 className="text-lg font-medium text-slate-300 mb-2">No plans found</h3>
          <p className="text-slate-500 max-w-sm mb-6">Create your first AI-driven QA plan to start generating comprehensive test suites.</p>
          <Button onClick={() => navigate('/plans/new')} variant="outline">Create a Plan</Button>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {plans.map((plan) => (
            <Card 
              key={plan.id} 
              className="cursor-pointer hover:-translate-y-1 hover:shadow-2xl hover:border-indigo-500/30 transition-all duration-300 group"
              onClick={() => navigate(`/plans/${plan.id}`)}
            >
              <div className="flex justify-between items-start mb-4">
                <Badge variant={getStatusVariant(plan.status)} className="uppercase">
                  {plan.status}
                </Badge>
                <button 
                  onClick={(e) => handleDelete(e, plan.id)}
                  className="opacity-0 group-hover:opacity-100 text-slate-500 hover:text-red-400 transition-opacity p-1"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
              <h3 className="text-lg font-semibold text-slate-200 mb-2 line-clamp-2" title={plan.title}>
                {plan.title}
              </h3>
              <div className="text-sm text-slate-500 space-y-1">
                <p>Version: {plan.current_version}</p>
                <p>Created: {new Date(plan.created_at).toLocaleDateString()}</p>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};
