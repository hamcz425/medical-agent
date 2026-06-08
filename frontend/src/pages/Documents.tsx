import React, { useEffect, useState } from 'react';
import {
  Table, Button, Space, Tag, Modal, Form, Input, Select,
  message, Popconfirm, Card, Upload, Tooltip
} from 'antd';
import {
  PlusOutlined, UploadOutlined, DeleteOutlined,
  EditOutlined, SearchOutlined, FileTextOutlined
} from '@ant-design/icons';
import { documentAPI, DocumentListResponse } from '../api';
import { MedicalDocument } from '../types';

const { Option } = Select;
const { TextArea } = Input;

const Documents: React.FC = () => {
  const [documents, setDocuments] = useState<MedicalDocument[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [isUploadModalVisible, setIsUploadModalVisible] = useState(false);
  const [editingDocument, setEditingDocument] = useState<MedicalDocument | null>(null);
  const [form] = Form.useForm();
  const [uploadForm] = Form.useForm();
  const [searchText, setSearchText] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string | undefined>();
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    fetchDocuments();
  }, [page, categoryFilter]);

  const fetchDocuments = async () => {
    setLoading(true);
    try {
      const result = await documentAPI.getAll(page, 10, categoryFilter, searchText);
      setDocuments(result.documents);
      setTotal(result.total);
    } catch (error: unknown) {
      if ((error as { response?: { status?: number } }).response?.status === 401) {
        message.error('请先登录');
      } else {
        message.error('获取文档列表失败');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = () => {
    setEditingDocument(null);
    form.resetFields();
    setIsModalVisible(true);
  };

  const handleEdit = (record: MedicalDocument) => {
    setEditingDocument(record);
    form.setFieldsValue(record);
    setIsModalVisible(true);
  };

  const handleDelete = async (id: string) => {
    try {
      await documentAPI.delete(id);
      message.success('删除成功');
      fetchDocuments();
    } catch (error: unknown) {
      message.error((error as { response?: { data?: { detail?: string } } }).response?.data?.detail || '删除失败');
    }
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      if (editingDocument) {
        await documentAPI.update(editingDocument.id.toString(), values);
        message.success('更新成功');
      } else {
        await documentAPI.create({
          ...values,
          metadata_json: {}
        });
        message.success('创建成功');
      }
      setIsModalVisible(false);
      fetchDocuments();
    } catch (error: unknown) {
      message.error((error as { response?: { data?: { detail?: string } } }).response?.data?.detail || '操作失败');
    }
  };

  const handleUpload = async () => {
    try {
      const values = await uploadForm.validateFields();
      const fileList = values.file;
      if (!fileList || fileList.length === 0) {
        message.warning('请选择文件');
        return;
      }

      setUploading(true);
      let successCount = 0;
      let failCount = 0;

      for (const fileItem of fileList) {
        const file = fileItem.originFileObj || fileItem;
        const formData = new FormData();
        formData.append('file', file);
        formData.append('category', values.category);
        if (values.source) {
          formData.append('source', values.source);
        }

        try {
          await documentAPI.upload(formData);
          successCount++;
        } catch {
          failCount++;
        }
      }

      if (successCount > 0) {
        message.success(`成功上传 ${successCount} 个文件`);
      }
      if (failCount > 0) {
        message.error(`${failCount} 个文件上传失败`);
      }

      setIsUploadModalVisible(false);
      uploadForm.resetFields();
      fetchDocuments();
    } catch {
      message.error('上传失败');
    } finally {
      setUploading(false);
    }
  };

  const handleSearch = () => {
    setPage(1);
    fetchDocuments();
  };

  const columns = [
    {
      title: '文档标题',
      dataIndex: 'title',
      key: 'title',
      render: (text: string) => <span>{text}</span>
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      render: (category: string) => {
        const colorMap: Record<string, string> = {
          medical_record: 'blue',
          research_paper: 'green',
          drug_info: 'orange',
          clinical_guide: 'purple'
        };
        const labelMap: Record<string, string> = {
          medical_record: '病历',
          research_paper: '研究论文',
          drug_info: '药物信息',
          clinical_guide: '临床指南'
        };
        return <Tag color={colorMap[category]}>{labelMap[category]}</Tag>;
      }
    },
    {
      title: '来源',
      dataIndex: 'source',
      key: 'source',
      render: (text: string) => text || '-'
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const colorMap: Record<string, string> = {
          pending: 'warning',
          processed: 'success',
          indexed: 'blue'
        };
        const labelMap: Record<string, string> = {
          pending: '待处理',
          processed: '已处理',
          indexed: '已索引'
        };
        return <Tag color={colorMap[status]}>{labelMap[status]}</Tag>;
      }
    },
    {
      title: '分块数',
      dataIndex: 'chunk_count',
      key: 'chunk_count',
      render: (count: number) => count || 0
    },
    {
      title: '操作',
      key: 'action',
      render: (_: unknown, record: MedicalDocument) => (
        <Space size="middle">
          <Tooltip title="编辑">
            <Button
              type="link"
              icon={<EditOutlined />}
              onClick={() => handleEdit(record)}
            />
          </Tooltip>
          <Popconfirm
            title="确定删除这个文档吗？"
            onConfirm={() => handleDelete(record.id.toString())}
            okText="确定"
            cancelText="取消"
          >
            <Tooltip title="删除">
              <Button type="link" danger icon={<DeleteOutlined />} />
            </Tooltip>
          </Popconfirm>
        </Space>
      )
    }
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between' }}>
          <Space>
            <Input
              placeholder="搜索文档"
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              onPressEnter={handleSearch}
              style={{ width: 300 }}
            />
            <Select
              placeholder="选择分类"
              allowClear
              style={{ width: 150 }}
              value={categoryFilter}
              onChange={(value) => { setCategoryFilter(value); setPage(1); }}
            >
              <Option value="medical_record">病历</Option>
              <Option value="research_paper">研究论文</Option>
              <Option value="drug_info">药物信息</Option>
              <Option value="clinical_guide">临床指南</Option>
            </Select>
            <Button
              type="primary"
              icon={<SearchOutlined />}
              onClick={handleSearch}
            >
              搜索
            </Button>
          </Space>
          <Space>
            <Button
              icon={<UploadOutlined />}
              onClick={() => {
                uploadForm.resetFields();
                setIsUploadModalVisible(true);
              }}
            >
              上传文件
            </Button>
            <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
              添加文档
            </Button>
          </Space>
        </div>

        <Table
          columns={columns}
          dataSource={documents}
          rowKey="id"
          loading={loading}
          pagination={{
            current: page,
            pageSize: 10,
            total: total,
            onChange: setPage,
            showSizeChanger: false,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条记录`
          }}
        />
      </Card>

      <Modal
        title={editingDocument ? '编辑文档' : '添加文档'}
        open={isModalVisible}
        onOk={handleSubmit}
        onCancel={() => setIsModalVisible(false)}
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="title"
            label="文档标题"
            rules={[{ required: true, message: '请输入文档标题' }]}
          >
            <Input placeholder="请输入文档标题" />
          </Form.Item>

          <Form.Item
            name="category"
            label="文档分类"
            rules={[{ required: true, message: '请选择文档分类' }]}
          >
            <Select placeholder="请选择文档分类">
              <Option value="medical_record">病历</Option>
              <Option value="research_paper">研究论文</Option>
              <Option value="drug_info">药物信息</Option>
              <Option value="clinical_guide">临床指南</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="source"
            label="来源"
            rules={[{ required: true, message: '请输入来源' }]}
          >
            <Input placeholder="请输入来源" />
          </Form.Item>

          <Form.Item
            name="content"
            label="内容"
            rules={[{ required: true, message: '请输入内容' }]}
          >
            <TextArea rows={6} placeholder="请输入文档内容" />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="上传文件"
        open={isUploadModalVisible}
        onOk={handleUpload}
        onCancel={() => setIsUploadModalVisible(false)}
        width={500}
        confirmLoading={uploading}
      >
        <Form form={uploadForm} layout="vertical">
          <Form.Item
            name="category"
            label="文档分类"
            rules={[{ required: true, message: '请选择文档分类' }]}
          >
            <Select placeholder="请选择文档分类">
              <Option value="medical_record">病历</Option>
              <Option value="research_paper">研究论文</Option>
              <Option value="drug_info">药物信息</Option>
              <Option value="clinical_guide">临床指南</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="source"
            label="来源"
          >
            <Input placeholder="请输入来源（可选）" />
          </Form.Item>

          <Form.Item
            name="file"
            label="选择文件"
            rules={[{ required: true, message: '请选择文件' }]}
          >
            <Upload.Dragger
              multiple={true}
              accept=".txt,.md,.pdf,.docx"
              beforeUpload={() => false}
              maxCount={10}
            >
              <p className="ant-upload-drag-icon">
                <FileTextOutlined />
              </p>
              <p className="ant-upload-text">点击或拖拽文件到此处上传</p>
              <p className="ant-upload-hint">
                支持 .txt, .md, .pdf, .docx 格式，单次最多上传10个文件
              </p>
            </Upload.Dragger>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Documents;
