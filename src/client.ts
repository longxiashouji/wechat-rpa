/**
 * 微信 RPA 机器人 - TypeScript 客户端
 *
 * 本模块封装了与 RPA 后端服务 (service.exe) 的所有 HTTP API 交互。
 * 基于 openapi.json 定义，使用 X-API-Key 进行认证。
 */

import axios, { AxiosInstance, AxiosError } from 'axios';

// API 配置
const API_BASE_URL = 'http://127.0.0.1:9922';
const API_KEY = 'yoko_test';

// 请求配置工厂
const createRequestConfig = () => ({
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY,
  },
  timeout: 60000, // 60秒超时，长时间任务可能需要更久
});

// 联系人数据结构
export interface Contact {
  name: string;
  wxid: string;
  tags: string[];
  is_new: boolean;
}

// 发送消息请求
export interface SendMessageRequest {
  user: string;
  message: string;
  account_id?: string;
}

// 发送文件请求
export interface SendFileRequest {
  user: string;
  file_path: string;
  account_id?: string;
}

// 发布朋友圈请求
export interface PostMomentRequest {
  content: string;
  files: string[];
}

// 群发任务请求
export interface MassSendingRequest {
  tags?: string[];
  targets?: string[];
  greeting_group: string;
  schedule_time?: string;
  batch_size?: number;
  account_id?: string;
}

// 激活码请求
export interface ActivationRequest {
  activation_code: string;
  machine_code: string;
}

// 工具类：禁用代理的 axios 实例
function createNoProxyAxios(): AxiosInstance {
  return axios.create({
    baseURL: API_BASE_URL,
    proxy: false, // 禁用代理，localhost 调用需要
  });
}

// 核心客户端类
export class WeChatRPAClient {
  private client: AxiosInstance;

  constructor() {
    this.client = createNoProxyAxios();
  }

  // ==================== 许可证相关 ====================

  /**
   * 获取机器码
   */
  async getMachineCode(): Promise<string> {
    const response = await this.client.get('/api/license/machine-code');
    return response.data.machine_code || response.data;
  }

  /**
   * 激活软件
   */
  async activateLicense(req: ActivationRequest): Promise<boolean> {
    try {
      const response = await this.client.post(
        '/api/license/activate',
        req,
        createRequestConfig()
      );
      return response.data.success || response.status === 200;
    } catch (e) {
      const err = e as AxiosError;
      console.error('激活失败:', err.message);
      return false;
    }
  }

  /**
   * 验证许可证状态
   */
  async verifyLicense(): Promise<any> {
    const response = await this.client.get('/api/license/verify');
    return response.data;
  }

  // ==================== 初始化相关 ====================

  /**
   * 获取 RPA 后端运行状态
   */
  async getBackendStatus(): Promise<any> {
    const response = await this.client.get(
      '/api/agent/backend_status',
      createRequestConfig()
    );
    return response.data;
  }

  /**
   * 获取微信实例状态
   */
  async getInstancesStatus(): Promise<any> {
    const response = await this.client.get(
      '/api/agent/instances_status',
      createRequestConfig()
    );
    return response.data;
  }

  /**
   * 初始化 RPA 服务并绑定微信
   * 这是所有操作的第一步
   */
  async initialize(): Promise<{ success: boolean; code?: string; message?: string }> {
    try {
      const response = await this.client.post(
        '/api/init/multi',
        {},
        createRequestConfig()
      );
      return { success: true, ...response.data };
    } catch (e) {
      const err = e as AxiosError;
      if (err.response) {
        const status = err.response.status;
        const data = err.response.data || {};
        if (status === 401) {
          return { success: false, code: 'UNAUTHORIZED' };
        }
        return { success: false, code: data.code || 'ERROR', message: data.message };
      }
      return { success: false, code: 'NETWORK_ERROR' };
    }
  }

  /**
   * 自动配置微信环境（危险操作）
   * 仅在 initialize() 返回 ENV_NOT_CONFIGURED 时调用
   */
  async autoConfig(): Promise<boolean> {
    try {
      const response = await this.client.post(
        '/api/system/wechat41/auto_config',
        {},
        createRequestConfig()
      );
      return response.status === 200;
    } catch (e) {
      console.error('自动配置失败:', (e as AxiosError).message);
      return false;
    }
  }

  // ==================== 消息相关 ====================

  /**
   * 发送文本消息
   * @param user 接收消息的联系人备注名/昵称/微信号
   * @param message 消息内容
   * @param account_id 发送方微信实例ID（多账号时使用）
   */
  async sendMessage(user: string, message: string, account_id?: string): Promise<boolean> {
    try {
      const req: SendMessageRequest = { user, message };
      if (account_id) req.account_id = account_id;

      const response = await this.client.post(
        '/api/chat/send_message',
        req,
        createRequestConfig()
      );
      return response.status === 200;
    } catch (e) {
      console.error('发送消息失败:', (e as AxiosError).message);
      return false;
    }
  }

  /**
   * 发送文件（图片/视频/文档）
   */
  async sendFile(user: string, file_path: string, account_id?: string): Promise<boolean> {
    try {
      const req: SendFileRequest = { user, file_path };
      if (account_id) req.account_id = account_id;

      const response = await this.client.post(
        '/api/agent/chat/send_file',
        req,
        createRequestConfig()
      );
      return response.status === 200;
    } catch (e) {
      console.error('发送文件失败:', (e as AxiosError).message);
      return false;
    }
  }

  /**
   * 获取聊天消息记录
   */
  async getMessages(sessionName: string, account_id?: string): Promise<any[]> {
    try {
      const params: any = {};
      if (account_id) params.account_id = account_id;

      const response = await this.client.get(
        `/api/chat/messages/${encodeURIComponent(sessionName)}`,
        { ...createRequestConfig(), params }
      );
      return response.data.messages || response.data;
    } catch (e) {
      console.error('获取消息失败:', (e as AxiosError).message);
      return [];
    }
  }

  // ==================== 朋友圈相关 ====================

  /**
   * 发布朋友圈
   */
  async postMoment(content: string, files: string[] = []): Promise<boolean> {
    try {
      const req: PostMomentRequest = { content, files };
      const response = await this.client.post(
        '/api/agent/post_moment',
        req,
        createRequestConfig()
      );
      return response.status === 200;
    } catch (e) {
      console.error('发布朋友圈失败:', (e as AxiosError).message);
      return false;
    }
  }

  // ==================== 群发相关 ====================

  /**
   * 创建群发任务
   */
  async massSending(req: MassSendingRequest): Promise<boolean> {
    try {
      const response = await this.client.post(
        '/api/agent/mass_sending',
        req,
        createRequestConfig()
      );
      return response.status === 200;
    } catch (e) {
      console.error('创建群发任务失败:', (e as AxiosError).message);
      return false;
    }
  }

  /**
   * 获取任务列表
   */
  async getTasks(): Promise<any[]> {
    try {
      const response = await this.client.get(
        '/api/agent/tasks',
        createRequestConfig()
      );
      return response.data.tasks || response.data;
    } catch (e) {
      console.error('获取任务列表失败:', (e as AxiosError).message);
      return [];
    }
  }

  // ==================== 联系人相关 ====================

  /**
   * 获取联系人列表（已同步的）
   * 注意：这个是已同步的数据，不是实时从微信获取
   */
  async getContacts(tag?: string, keyword?: string, account_id?: string): Promise<Contact[]> {
    try {
      const params: any = {};
      if (tag) params.tag = tag;
      if (keyword) params.keyword = keyword;
      if (account_id) params.account_id = account_id;

      const response = await this.client.get(
        '/api/contacts',
        { ...createRequestConfig(), params }
      );
      return response.data || [];
    } catch (e) {
      console.error('获取联系人失败:', (e as AxiosError).message);
      return [];
    }
  }

  /**
   * 同步联系人（慢，~2分钟）
   * 仅在联系人数据过时时才需要调用
   */
  async syncContacts(type: 'friend' | 'group', account_id: string): Promise<boolean> {
    try {
      const response = await this.client.post(
        '/api/contact/sync',
        { type, account_id },
        createRequestConfig()
      );
      return response.status === 200;
    } catch (e) {
      console.error('同步联系人失败:', (e as AxiosError).message);
      return false;
    }
  }

  // ==================== AI 功能开关 ====================

  /**
   * 获取 AI 功能状态
   */
  async getFeaturesStatus(): Promise<any> {
    try {
      const response = await this.client.get(
        '/api/agent/features_status',
        createRequestConfig()
      );
      return response.data;
    } catch (e) {
      console.error('获取功能状态失败:', (e as AxiosError).message);
      return {};
    }
  }

  /**
   * 开启 AI 销售监控
   */
  async startAIMonitor(): Promise<boolean> {
    try {
      const response = await this.client.post(
        '/api/chat/multi-monitor/start',
        {},
        createRequestConfig()
      );
      return response.status === 200;
    } catch (e) {
      console.error('开启AI监控失败:', (e as AxiosError).message);
      return false;
    }
  }

  /**
   * 停止 AI 销售监控
   */
  async stopAIMonitor(): Promise<boolean> {
    try {
      const response = await this.client.post(
        '/api/chat/monitor/stop',
        {},
        createRequestConfig()
      );
      return response.status === 200;
    } catch (e) {
      console.error('停止AI监控失败:', (e as AxiosError).message);
      return false;
    }
  }

  /**
   * 开启/关闭自动通过好友
   */
  async toggleAutoAddFriend(enabled: boolean): Promise<boolean> {
    try {
      const response = await this.client.post(
        '/api/friend/auto-add-new/toggle',
        { enabled },
        createRequestConfig()
      );
      return response.status === 200;
    } catch (e) {
      console.error('切换自动加好友失败:', (e as AxiosError).message);
      return false;
    }
  }

  /**
   * 开启/关闭朋友圈自动评论
   */
  async toggleAutoComment(enabled: boolean): Promise<boolean> {
    try {
      const response = await this.client.post(
        '/api/moment/toggle-auto-comment',
        { enabled },
        createRequestConfig()
      );
      return response.status === 200;
    } catch (e) {
      console.error('切换朋友圈自动评论失败:', (e as AxiosError).message);
      return false;
    }
  }

  // ==================== 配置相关 ====================

  /**
   * 获取配置
   */
  async getConfig(configType: string): Promise<any> {
    try {
      const response = await this.client.get(
        `/api/config/${configType}`,
        createRequestConfig()
      );
      return response.data;
    } catch (e) {
      console.error('获取配置失败:', (e as AxiosError).message);
      return null;
    }
  }

  /**
   * 更新配置
   */
  async updateConfig(configType: string, config: any): Promise<boolean> {
    try {
      const response = await this.client.post(
        `/api/config/${configType}`,
        config,
        createRequestConfig()
      );
      return response.status === 200;
    } catch (e) {
      console.error('更新配置失败:', (e as AxiosError).message);
      return false;
    }
  }
}

// 导出单例
export const wechatClient = new WeChatRPAClient();
export default wechatClient;