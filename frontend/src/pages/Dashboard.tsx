import React, { useEffect, useState } from 'react';
import { Card, Col, Row, Statistic, Table, Tag, Progress, Empty, Spin, message } from 'antd';
import {
  FileTextOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  RobotOutlined
} from '@ant-design/icons';
import { ragAPI, SystemStats } from '../api';

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const data = await ragAPI.getStats();
      setStats(data);
    } catch (error: unknown) {
      if ((error as { response?: { status?: number } }).response?.status === 401) {
        message.error('请先登录');
      } else {
        message.error('获取统计数据失败');
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '24px', textAlign: 'center' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!stats) {
    return (
      <div style={{ padding: '24px' }}>
        <Empty description="无法加载数据" />
      </div>
    );
  }

  const columns = [
    {
      title: '查询内容',
      dataIndex: 'query',
      key: 'query',
      render: (text: string) => <span>{text}</span>
    },
    {
      title: '置信度',
      dataIndex: 'confidence',
      key: 'confidence',
      render: (confidence: number) => (
        <Tag color={confidence > 80 ? 'success' : confidence > 60 ? 'warning' : 'error'}>
          {confidence.toFixed(1)}%
        </Tag>
      )
    },
    {
      title: '响应时间',
      dataIndex: 'processing_time',
      key: 'processing_time',
      render: (time: number) => time ? `${time}ms` : '-'
    }
  ];

  return (
    <div style={{ padding: '24px' }}>
      <h2 style={{ marginBottom: '24px' }}>系统概览</h2>

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总文档数"
              value={stats.total_documents}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="已处理文档"
              value={stats.processed_documents}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="已索引文档"
              value={stats.indexed_documents}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总查询次数"
              value={stats.total_queries}
              prefix={<RobotOutlined />}
              valueStyle={{ color: '#fa8c16' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: '24px' }}>
        <Col xs={24} lg={12}>
          <Card title="系统健康状态">
            <div style={{ textAlign: 'center', padding: '20px' }}>
              <Progress
                type="dashboard"
                percent={stats.system_health === 'healthy' ? 100 : stats.system_health === 'warning' ? 60 : 20}
                strokeColor={stats.system_health === 'healthy' ? '#52c41a' : stats.system_health === 'warning' ? '#faad14' : '#ff4d4f'}
              />
              <div style={{ marginTop: '16px' }}>
                <Tag color={stats.system_health === 'healthy' ? 'success' : stats.system_health === 'warning' ? 'warning' : 'error'}>
                  {stats.system_health === 'healthy' ? '系统正常' : stats.system_health === 'warning' ? '系统警告' : '系统异常'}
                </Tag>
              </div>
            </div>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="平均响应时间">
            <div style={{ textAlign: 'center', padding: '20px' }}>
              <Statistic
                value={stats.average_response_time}
                suffix="ms"
                valueStyle={{ fontSize: '48px', color: '#1890ff' }}
              />
              <div style={{ marginTop: '16px', color: '#666' }}>
                RAG查询平均响应时间
              </div>
            </div>
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: '24px' }}>
        <Col xs={24} lg={12}>
          <Card title="文档分类统计">
            {Object.keys(stats.document_categories || {}).length > 0 ? (
              <div style={{ padding: '20px' }}>
                {Object.entries(stats.document_categories || {}).map(([category, count]) => {
                  const labelMap: Record<string, string> = {
                    medical_record: '病历',
                    research_paper: '研究论文',
                    drug_info: '药物信息',
                    clinical_guide: '临床指南'
                  };
                  return (
                    <div key={category} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                      <Tag>{labelMap[category] || category}</Tag>
                      <span style={{ fontWeight: 'bold' }}>{count as number}</span>
                    </div>
                  );
                })}
              </div>
            ) : (
              <Empty description="暂无数据" />
            )}
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="最近查询">
            {stats.recent_queries && stats.recent_queries.length > 0 ? (
              <Table
                columns={columns}
                dataSource={stats.recent_queries}
                rowKey="id"
                pagination={false}
                size="small"
              />
            ) : (
              <Empty description="暂无查询记录" />
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
