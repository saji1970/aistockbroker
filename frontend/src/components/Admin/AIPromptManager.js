import React, { useState, useEffect } from 'react';
import {
  PlusIcon,
  PencilIcon,
  TrashIcon,
  CheckIcon,
  XMarkIcon,
  SparklesIcon,
  DocumentTextIcon,
  TagIcon
} from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';

const AIPromptManager = () => {
  const [prompts, setPrompts] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingPrompt, setEditingPrompt] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterCategory, setFilterCategory] = useState('all');

  const [newPrompt, setNewPrompt] = useState({
    title: '',
    category: 'general',
    prompt: '',
    response_template: '',
    tags: [],
    is_active: true
  });

  const categories = [
    { value: 'general', label: 'General', color: 'blue' },
    { value: 'stock_analysis', label: 'Stock Analysis', color: 'green' },
    { value: 'trading_strategy', label: 'Trading Strategy', color: 'purple' },
    { value: 'portfolio_management', label: 'Portfolio Management', color: 'orange' },
    { value: 'market_insights', label: 'Market Insights', color: 'red' },
    { value: 'risk_assessment', label: 'Risk Assessment', color: 'yellow' }
  ];

  const commonTags = [
    'beginner', 'advanced', 'technical', 'fundamental', 'short-term', 'long-term',
    'high-risk', 'low-risk', 'dividend', 'growth', 'value', 'momentum'
  ];

  // Load prompts on component mount
  useEffect(() => {
    loadPrompts();
  }, []);

  const loadPrompts = async () => {
    setIsLoading(true);
    try {
      // Mock data for now - replace with actual API call
      const mockPrompts = [
        {
          id: 1,
          title: 'Stock Price Analysis',
          category: 'stock_analysis',
          prompt: 'Analyze the current stock price of {symbol} and provide insights on its performance.',
          response_template: 'Based on my analysis of {symbol}, here are the key insights...',
          tags: ['technical', 'fundamental'],
          is_active: true,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z'
        },
        {
          id: 2,
          title: 'Trading Strategy Recommendation',
          category: 'trading_strategy',
          prompt: 'Recommend a trading strategy for {symbol} based on current market conditions.',
          response_template: 'For {symbol}, I recommend the following strategy...',
          tags: ['strategy', 'risk-management'],
          is_active: true,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z'
        }
      ];
      setPrompts(mockPrompts);
    } catch (error) {
      console.error('Error loading prompts:', error);
      toast.error('Failed to load AI prompts');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddPrompt = async () => {
    try {
      // Mock API call - replace with actual implementation
      const promptData = {
        ...newPrompt,
        id: Date.now(),
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
      
      setPrompts([...prompts, promptData]);
      setNewPrompt({
        title: '',
        category: 'general',
        prompt: '',
        response_template: '',
        tags: [],
        is_active: true
      });
      setShowAddModal(false);
      toast.success('AI prompt added successfully');
    } catch (error) {
      console.error('Error adding prompt:', error);
      toast.error('Failed to add AI prompt');
    }
  };

  const handleUpdatePrompt = async (id, updatedData) => {
    try {
      // Mock API call - replace with actual implementation
      setPrompts(prompts.map(prompt => 
        prompt.id === id 
          ? { ...prompt, ...updatedData, updated_at: new Date().toISOString() }
          : prompt
      ));
      setEditingPrompt(null);
      toast.success('AI prompt updated successfully');
    } catch (error) {
      console.error('Error updating prompt:', error);
      toast.error('Failed to update AI prompt');
    }
  };

  const handleDeletePrompt = async (id) => {
    if (!window.confirm('Are you sure you want to delete this AI prompt?')) {
      return;
    }

    try {
      // Mock API call - replace with actual implementation
      setPrompts(prompts.filter(prompt => prompt.id !== id));
      toast.success('AI prompt deleted successfully');
    } catch (error) {
      console.error('Error deleting prompt:', error);
      toast.error('Failed to delete AI prompt');
    }
  };

  const handleToggleActive = async (id) => {
    const prompt = prompts.find(p => p.id === id);
    if (prompt) {
      await handleUpdatePrompt(id, { is_active: !prompt.is_active });
    }
  };

  const filteredPrompts = prompts.filter(prompt => {
    const matchesSearch = prompt.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         prompt.prompt.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = filterCategory === 'all' || prompt.category === filterCategory;
    return matchesSearch && matchesCategory;
  });

  const getCategoryInfo = (category) => {
    return categories.find(cat => cat.value === category) || { label: 'General', color: 'blue' };
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-600 rounded-lg flex items-center justify-center">
              <SparklesIcon className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">AI Prompt Manager</h1>
              <p className="text-gray-600">Manage AI assistant training prompts and responses</p>
            </div>
          </div>
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <PlusIcon className="w-5 h-5" />
            <span>Add Prompt</span>
          </button>
        </div>

        {/* Filters */}
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Search prompts..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <select
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">All Categories</option>
            {categories.map(category => (
              <option key={category.value} value={category.value}>
                {category.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Prompts List */}
      <div className="grid gap-4">
        {isLoading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-2 text-gray-600">Loading prompts...</p>
          </div>
        ) : filteredPrompts.length === 0 ? (
          <div className="text-center py-8">
            <DocumentTextIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">No prompts found</p>
          </div>
        ) : (
          filteredPrompts.map((prompt) => (
            <div key={prompt.id} className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">{prompt.title}</h3>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      getCategoryInfo(prompt.category).color === 'blue' ? 'bg-blue-100 text-blue-800' :
                      getCategoryInfo(prompt.category).color === 'green' ? 'bg-green-100 text-green-800' :
                      getCategoryInfo(prompt.category).color === 'purple' ? 'bg-purple-100 text-purple-800' :
                      getCategoryInfo(prompt.category).color === 'orange' ? 'bg-orange-100 text-orange-800' :
                      getCategoryInfo(prompt.category).color === 'red' ? 'bg-red-100 text-red-800' :
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {getCategoryInfo(prompt.category).label}
                    </span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      prompt.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {prompt.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                  
                  <div className="space-y-3">
                    <div>
                      <label className="text-sm font-medium text-gray-700">Prompt Template:</label>
                      <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded border">
                        {prompt.prompt}
                      </p>
                    </div>
                    
                    <div>
                      <label className="text-sm font-medium text-gray-700">Response Template:</label>
                      <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded border">
                        {prompt.response_template}
                      </p>
                    </div>
                    
                    {prompt.tags.length > 0 && (
                      <div>
                        <label className="text-sm font-medium text-gray-700">Tags:</label>
                        <div className="flex flex-wrap gap-2 mt-1">
                          {prompt.tags.map((tag, index) => (
                            <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                              {tag}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
                
                <div className="flex items-center space-x-2 ml-4">
                  <button
                    onClick={() => setEditingPrompt(prompt)}
                    className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                    title="Edit prompt"
                  >
                    <PencilIcon className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleToggleActive(prompt.id)}
                    className={`p-2 rounded-lg transition-colors ${
                      prompt.is_active 
                        ? 'text-green-600 hover:bg-green-50' 
                        : 'text-gray-400 hover:bg-gray-50'
                    }`}
                    title={prompt.is_active ? 'Deactivate' : 'Activate'}
                  >
                    <CheckIcon className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDeletePrompt(prompt.id)}
                    className="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    title="Delete prompt"
                  >
                    <TrashIcon className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Add/Edit Modal */}
      {(showAddModal || editingPrompt) && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-gray-900">
                  {editingPrompt ? 'Edit AI Prompt' : 'Add New AI Prompt'}
                </h2>
                <button
                  onClick={() => {
                    setShowAddModal(false);
                    setEditingPrompt(null);
                    setNewPrompt({
                      title: '',
                      category: 'general',
                      prompt: '',
                      response_template: '',
                      tags: [],
                      is_active: true
                    });
                  }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XMarkIcon className="w-6 h-6" />
                </button>
              </div>

              <form onSubmit={(e) => {
                e.preventDefault();
                if (editingPrompt) {
                  handleUpdatePrompt(editingPrompt.id, newPrompt);
                } else {
                  handleAddPrompt();
                }
              }} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Title *
                  </label>
                  <input
                    type="text"
                    value={newPrompt.title}
                    onChange={(e) => setNewPrompt({...newPrompt, title: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Enter prompt title"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Category *
                  </label>
                  <select
                    value={newPrompt.category}
                    onChange={(e) => setNewPrompt({...newPrompt, category: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  >
                    {categories.map(category => (
                      <option key={category.value} value={category.value}>
                        {category.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Prompt Template *
                  </label>
                  <textarea
                    value={newPrompt.prompt}
                    onChange={(e) => setNewPrompt({...newPrompt, prompt: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    rows={3}
                    placeholder="Enter the prompt template (use {symbol} for dynamic values)"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Response Template *
                  </label>
                  <textarea
                    value={newPrompt.response_template}
                    onChange={(e) => setNewPrompt({...newPrompt, response_template: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    rows={4}
                    placeholder="Enter the response template"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Tags
                  </label>
                  <div className="flex flex-wrap gap-2 mb-2">
                    {commonTags.map(tag => (
                      <button
                        key={tag}
                        type="button"
                        onClick={() => {
                          const newTags = newPrompt.tags.includes(tag)
                            ? newPrompt.tags.filter(t => t !== tag)
                            : [...newPrompt.tags, tag];
                          setNewPrompt({...newPrompt, tags: newTags});
                        }}
                        className={`px-3 py-1 rounded-full text-sm transition-colors ${
                          newPrompt.tags.includes(tag)
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        {tag}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="is_active"
                    checked={newPrompt.is_active}
                    onChange={(e) => setNewPrompt({...newPrompt, is_active: e.target.checked})}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor="is_active" className="ml-2 text-sm text-gray-700">
                    Active (prompt will be used by AI assistant)
                  </label>
                </div>

                <div className="flex justify-end space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={() => {
                      setShowAddModal(false);
                      setEditingPrompt(null);
                    }}
                    className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    {editingPrompt ? 'Update Prompt' : 'Add Prompt'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AIPromptManager;
