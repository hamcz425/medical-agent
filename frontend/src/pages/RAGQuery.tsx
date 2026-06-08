import React, { useState, useEffect } from 'react';
import {
  Card, Input, Button, List, Tag, Space, Typography,
  Spin, Alert, Divider, Progress, Empty, message, Radio, Tooltip
} from 'antd';
import {
  SendOutlined, RobotOutlined, UserOutlined,
  FileTextOutlined, ClockCircleOutlined, HistoryOutlined,
  CheckCircleOutlined, CloseCircleOutlined,
  LikeOutlined, DislikeOutlined, EditOutlined
} from '@ant-design/icons';
import { ragAPI } from '../api';
import { RAGQuery as RAGQueryType } from '../types';
import { loadSettings } from './Settings';

const { TextArea } = Input;
const { Text, Paragraph } = Typography;

const RETRIEVAL_MODES = [
  { value: 'hybrid', label: '混合检索', desc: 'BM25 + 向量语义，效果最好' },
  { value: 'vector', label: '向量检索', desc: '纯语义相似度匹配' },
  { value: 'bm25', label: '关键词检索', desc: 'BM25 关键词匹配' },
];

const RAGQueryPage: React.FC = () => {
  const [query, setQuery] = useState('');
  const [queries, setQueries] = useState<RAGQueryType[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedQuery, setSelectedQuery] = useState<RAGQueryType | null>(null);
  const [retrievalMode, setRetrievalMode] = useState<string>(() => loadSettings().defaultRetrievalMode || 'hybrid');
  const [feedbackMap, setFeedbackMap] = useState<Record<string, { rating?: string; comment?: string }>>({});

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const result = await ragAPI.getHistory(20);
      if (result.queries) {
        setQueries(result.queries);
      }
    } catch {
      message.error('加载历史记录失败');
    }
  };

  const handleQuery = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const result = await ragAPI.query(query, 5, retrievalMode);
      setQueries(prev => [result, ...prev]);
      setSelectedQuery(result);
      setQuery('');
    } catch (error: unknown) {
      if ((error as { response?: { status?: number } }).response?.status === 401) {
        message.error('请先登录');
      } else {
        setError('查询失败，请稍后重试');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleQuery();
    }
  };

  const handleSelectQuery = (item: RAGQueryType) => {
    setSelectedQuery(item);
  };

  const handleFeedback = async (queryId: string, rating: string) => {
    const current = feedbackMap[queryId];
    if (current?.rating === rating) return;

    try {
      await ragAPI.submitFeedback(Number(queryId), rating);
      setFeedbackMap(prev => ({
        ...prev,
        [queryId]: { ...prev[queryId], rating }
      }));
      message.success('反馈已提交');
    } catch (err) {
      message.error('反馈提交失败');
    }
  };

  const getModeLabel = (mode?: string) => {
    return RETRIEVAL_MODES.find(m => m.value === mode)?.label || mode || '混合检索';
  };

  return (
    <div style={{ padding: '24px', height: '100%' }}>
      <div style={{ display: 'flex', height: 'calc(100vh - 160px)' }}>
        {/* 左侧：查询输入和历史 */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', marginRight: '24px' }}>
          <Card title="RAG智能查询" style={{ marginBottom: '16px' }}>
            <Paragraph type="secondary">
              基于医疗大语言模型的检索增强生成系统，输入您的医疗问题，系统将从知识库中检索相关信息并生成回答。
            </Paragraph>

            <TextArea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="请输入您的医疗问题，例如：糖尿病的治疗方法有哪些？"
              autoSize={{ minRows: 3, maxRows: 6 }}
              style={{ marginBottom: '16px' }}
            />

            <Space>
              <Radio.Group
                value={retrievalMode}
                onChange={(e) => setRetrievalMode(e.target.value)}
                optionType="button"
                buttonStyle="solid"
                size="small"
              >
                {RETRIEVAL_MODES.map(mode => (
                  <Radio.Button key={mode.value} value={mode.value}>
                    <Tooltip title={mode.desc}>{mode.label}</Tooltip>
                  </Radio.Button>
                ))}
              </Radio.Group>
            </Space>

            <div style={{ marginTop: '12px' }}>
              <Space>
                <Button
                  type="primary"
                  icon={<SendOutlined />}
                  onClick={handleQuery}
                  loading={loading}
                >
                  发送查询
                </Button>
                <Button onClick={() => setQuery('')}>
                  清空
                </Button>
              </Space>
            </div>
          </Card>

          {error && (
            <Alert
              message="查询错误"
              description={error}
              type="error"
              showIcon
              closable
              style={{ marginBottom: '16px' }}
              onClose={() => setError(null)}
            />
          )}

          <Card
            title={<Space><HistoryOutlined /> 查询历史</Space>}
            style={{ flex: 1, overflow: 'auto' }}
          >
            {queries.length > 0 ? (
              <List
                dataSource={queries}
                renderItem={(item) => (
                  <List.Item
                    style={{
                      cursor: 'pointer',
                      backgroundColor: selectedQuery?.id === item.id ? '#e6f7ff' : 'transparent',
                      padding: '12px',
                      borderRadius: '8px',
                      marginBottom: '8px'
                    }}
                    onClick={() => handleSelectQuery(item)}
                  >
                    <List.Item.Meta
                      avatar={<UserOutlined style={{ fontSize: '24px', color: '#1890ff' }} />}
                      title={
                        <Space>
                          <Text strong>{item.query}</Text>
                          <Tag color="blue">{(item.confidence || 0).toFixed(1)}%</Tag>
                          <Tag color="purple">{getModeLabel(item.retrieval_mode)}</Tag>
                        </Space>
                      }
                      description={
                        <div>
                          <Paragraph ellipsis={{ rows: 2 }}>{item.response}</Paragraph>
                          <Space>
                            <Text type="secondary">
                              <ClockCircleOutlined /> {(item.processing_time || 0)}ms
                            </Text>
                            <Text type="secondary">
                              <FileTextOutlined /> {item.sources?.length || 0} 个来源
                            </Text>
                            {item.verification && (
                              <Text type="secondary">
                                {item.verification.passed
                                  ? <><CheckCircleOutlined style={{ color: '#52c41a' }} /> 已验证</>
                                  : <><CloseCircleOutlined style={{ color: '#ff4d4f' }} /> 验证未通过</>
                                }
                              </Text>
                            )}
                          </Space>
                        </div>
                      }
                    />
                  </List.Item>
                )}
              />
            ) : (
              <Empty description="暂无查询历史" />
            )}
          </Card>
        </div>

        {/* 右侧：当前查询详情 */}
        <div style={{ width: '450px' }}>
          <Card title="查询详情" style={{ height: '100%' }}>
            {loading ? (
              <div style={{ textAlign: 'center', padding: '40px' }}>
                <Spin size="large" />
                <div style={{ marginTop: '16px' }}>正在处理查询...</div>
              </div>
            ) : selectedQuery ? (
              <div style={{ overflow: 'auto', maxHeight: 'calc(100vh - 250px)' }}>
                <div style={{ marginBottom: '16px' }}>
                  <Space>
                    <Tag color="purple">{getModeLabel(selectedQuery.retrieval_mode)}</Tag>
                    {selectedQuery.verification && (
                      selectedQuery.verification.passed
                        ? <Tag color="success"><CheckCircleOutlined /> 验证通过</Tag>
                        : <Tag color="error"><CloseCircleOutlined /> 验证未通过</Tag>
                    )}
                  </Space>
                </div>

                <div style={{ marginBottom: '24px' }}>
                  <Text strong>问题：</Text>
                  <Paragraph>{selectedQuery.query}</Paragraph>
                </div>

                <Divider />

                <div style={{ marginBottom: '24px' }}>
                  <Text strong>回答：</Text>
                  <Paragraph style={{ whiteSpace: 'pre-wrap' }}>{selectedQuery.response}</Paragraph>
                </div>

                {selectedQuery.verification && !selectedQuery.verification.passed && (
                  <>
                    <Alert
                      message="验证说明"
                      description={selectedQuery.verification.reason}
                      type="warning"
                      showIcon
                      style={{ marginBottom: '16px' }}
                    />
                    <Divider />
                  </>
                )}

                <div style={{ marginBottom: '24px' }}>
                  <Text strong>置信度：</Text>
                  <Progress
                    percent={selectedQuery.confidence || 0}
                    status={(selectedQuery.confidence || 0) > 80 ? 'success' : (selectedQuery.confidence || 0) > 60 ? 'normal' : 'exception'}
                  />
                </div>

                <Divider />

                <div style={{ marginBottom: '24px' }}>
                  <Text strong>参考来源：</Text>
                  {selectedQuery.sources && selectedQuery.sources.length > 0 ? (
                    <List
                      size="small"
                      dataSource={selectedQuery.sources}
                      renderItem={(source) => (
                        <List.Item>
                          <List.Item.Meta
                            avatar={<FileTextOutlined />}
                            title={source.title}
                            description={
                              <Space>
                                <Tag color="blue">{source.category}</Tag>
                                <Text type="secondary">{source.source}</Text>
                              </Space>
                            }
                          />
                        </List.Item>
                      )}
                    />
                  ) : (
                    <Text type="secondary">无参考来源</Text>
                  )}
                </div>

                <Divider />

                <div>
                  <Text strong>这个回答有帮助吗？</Text>
                  <div style={{ marginTop: '8px' }}>
                    <Space>
                      <Tooltip title="回答正确">
                        <Button
                          icon={<LikeOutlined />}
                          type={feedbackMap[selectedQuery.id]?.rating === 'correct' ? 'primary' : 'default'}
                          onClick={() => handleFeedback(selectedQuery.id, 'correct')}
                        >
                          正确
                        </Button>
                      </Tooltip>
                      <Tooltip title="回答有误">
                        <Button
                          icon={<DislikeOutlined />}
                          type={feedbackMap[selectedQuery.id]?.rating === 'incorrect' ? 'primary' : 'default'}
                          danger={feedbackMap[selectedQuery.id]?.rating === 'incorrect'}
                          onClick={() => handleFeedback(selectedQuery.id, 'incorrect')}
                        >
                          有误
                        </Button>
                      </Tooltip>
                      <Tooltip title="部分正确">
                        <Button
                          icon={<EditOutlined />}
                          type={feedbackMap[selectedQuery.id]?.rating === 'partial' ? 'primary' : 'default'}
                          onClick={() => handleFeedback(selectedQuery.id, 'partial')}
                        >
                          部分正确
                        </Button>
                      </Tooltip>
                    </Space>
                  </div>
                </div>
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
                <RobotOutlined style={{ fontSize: '48px', marginBottom: '16px' }} />
                <div>输入问题开始查询</div>
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
};

export default RAGQueryPage;
