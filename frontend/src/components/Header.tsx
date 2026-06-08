import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Layout, Menu, Avatar, Dropdown, Tag, Space } from 'antd';
import {
  DashboardOutlined,
  FileTextOutlined,
  RobotOutlined,
  SettingOutlined,
  UserOutlined,
  LogoutOutlined
} from '@ant-design/icons';

const { Header: AntHeader } = Layout;

const Header: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [user, setUser] = useState<{ username?: string; full_name?: string; role?: string } | null>(null);

  const selectedKey = location.pathname.replace('/', '') || 'dashboard';

  useEffect(() => {
    try {
      const storedUser = localStorage.getItem('user');
      if (storedUser) {
        setUser(JSON.parse(storedUser));
      }
    } catch {
      // invalid JSON in localStorage, ignore
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  const menuItems = [
    {
      key: 'dashboard',
      icon: <DashboardOutlined />,
      label: '数据概览'
    },
    {
      key: 'documents',
      icon: <FileTextOutlined />,
      label: '文档管理'
    },
    {
      key: 'rag',
      icon: <RobotOutlined />,
      label: 'RAG查询'
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '系统设置'
    }
  ];

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: (
        <Space direction="vertical" size={0}>
          <div style={{ fontWeight: 'bold' }}>{user?.full_name || user?.username || '用户'}</div>
          <Tag color="blue" style={{ fontSize: 11 }}>{user?.role || 'viewer'}</Tag>
        </Space>
      ),
      disabled: true
    },
    { type: 'divider' as const },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: handleLogout
    }
  ];

  const handleMenuClick = (info: { key: string }) => {
    navigate(`/${info.key}`);
  };

  return (
    <AntHeader style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      background: '#001529',
      padding: '0 24px'
    }}>
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <div style={{
          color: 'white',
          fontSize: '18px',
          fontWeight: 'bold',
          marginRight: '48px',
          cursor: 'pointer'
        }} onClick={() => navigate('/dashboard')}>
          医疗RAG系统
        </div>
        <Menu
          theme="dark"
          mode="horizontal"
          selectedKeys={[selectedKey]}
          items={menuItems}
          onClick={handleMenuClick}
          style={{ minWidth: '400px' }}
        />
      </div>
      <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
        <Space style={{ cursor: 'pointer' }}>
          <Avatar
            icon={<UserOutlined />}
            style={{ backgroundColor: '#1890ff' }}
          />
          <span style={{ color: 'white' }}>{user?.username || '用户'}</span>
        </Space>
      </Dropdown>
    </AntHeader>
  );
};

export default Header;
