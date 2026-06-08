import React, { useEffect } from 'react';
import { Card, Form, Input, Switch, Button, message, Divider, Space, Tag, InputNumber } from 'antd';
import { SaveOutlined, InfoCircleOutlined } from '@ant-design/icons';

export const SETTINGS_KEY = 'medical_rag_settings';

export interface SettingsData {
  apiEndpoint: string;
  enableCache: boolean;
  maxRetries: number;
  defaultRetrievalMode: string;
}

export const defaultSettings: SettingsData = {
  apiEndpoint: 'http://localhost:8000/api',
  enableCache: true,
  maxRetries: 3,
  defaultRetrievalMode: 'hybrid'
};

export function loadSettings(): SettingsData {
  const saved = localStorage.getItem(SETTINGS_KEY);
  if (saved) {
    try {
      return { ...defaultSettings, ...JSON.parse(saved) };
    } catch {
      return defaultSettings;
    }
  }
  return defaultSettings;
}

const Settings: React.FC = () => {
  const [form] = Form.useForm();

  useEffect(() => {
    form.setFieldsValue(loadSettings());
  }, [form]);

  const handleSave = (values: SettingsData) => {
    localStorage.setItem(SETTINGS_KEY, JSON.stringify(values));
    message.success('设置已保存');
  };

  return (
    <div style={{ padding: '24px' }}>
      <h2 style={{ marginBottom: '24px' }}>系统设置</h2>

      <Card title="基本设置" style={{ marginBottom: '16px' }}>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSave}
          initialValues={defaultSettings}
        >
          <Form.Item
            name="apiEndpoint"
            label="API端点"
            rules={[{ required: true, message: '请输入API端点' }]}
          >
            <Input placeholder="http://localhost:8000/api" />
          </Form.Item>

          <Form.Item
            name="defaultRetrievalMode"
            label="默认检索模式"
          >
            <Input placeholder="hybrid / vector / bm25" />
          </Form.Item>

          <Form.Item
            name="enableCache"
            label="启用缓存"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

          <Form.Item
            name="maxRetries"
            label="最大重试次数"
          >
            <InputNumber min={0} max={10} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" icon={<SaveOutlined />}>
              保存设置
            </Button>
          </Form.Item>
        </Form>
      </Card>

      <Card title="系统信息">
        <Space direction="vertical" size="middle" style={{ width: '100%' }}>
          <div>
            <InfoCircleOutlined style={{ marginRight: 8 }} />
            <span>设置保存在浏览器本地存储中，清除浏览器数据会重置设置。</span>
          </div>
          <Divider style={{ margin: '8px 0' }} />
          <Space wrap>
            <span>版本：</span>
            <Tag color="blue">v1.0.0</Tag>
            <span>检索模式：</span>
            <Tag color="green">BM25 + Vector Hybrid</Tag>
            <span>LLM：</span>
            <Tag color="purple">智谱 GLM-4-Flash</Tag>
            <span>Embedding：</span>
            <Tag color="orange">paraphrase-multilingual-MiniLM-L12-v2</Tag>
          </Space>
        </Space>
      </Card>
    </div>
  );
};

export default Settings;
