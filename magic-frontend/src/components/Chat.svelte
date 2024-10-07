<script>
  import { httpRequest } from './HttpRequest.svelte';
  import { selectedMode, selectedConnector, selectedDataset } from '../js/store.js';
  import RightPanel from './RightPanel.svelte';

  let messages = [];
  let input = '';
  let loadingMessage = false; // 加载状态

  function sendMessage() {
    if (input.trim()) {
      const userMessage = { text: input, user: 'me' };
      messages = [...messages, userMessage];
      input = '';
      agentProcess(userMessage.text);
    }
  }

  async function agentProcess(personInput) {
    loadingMessage = true; // 开始加载
    let body = {
      agent_type: $selectedMode,
      person_input: personInput
    };

    if ($selectedMode === "sql") {
      body["data_connector_id"] = $selectedConnector;
    } else if ($selectedMode === "rag") {
      body["dataset_id"] = $selectedDataset;
    }

    try {
      const ret = await httpRequest('/agent/process', 'POST', body);
      if (ret.code === 0) {
        messages = [...messages, { text: ret.data.answer, user: 'API' }];
      }
    } catch (error) {
      console.error(error);
      messages = [...messages, { text: '错误: ' + error.message, user: '系统' }];
    } finally {
      loadingMessage = false; // 加载完成
    }

    console.log(messages);
  }
</script>

<style>
  .chat-container {
    display: flex;
    height: 100%;
  }

  .chat-box {
    flex: 0 0 85%; /* 左侧占 85% */
    display: flex;
    flex-direction: column; /* 垂直布局 */
    border: 1px solid #ccc;
    border-radius: 8px;
    background-color: #f9f9f9;
  }

  .messages {
    flex: 1; /* 消息区域占据剩余空间 */
    overflow-y: auto; /* 仅消息区域可滚动 */
    padding: 10px;
  }

  .right-panel {
    flex: 0 0 15%; /* 右侧占 15% */
    padding: 10px;
    background-color: #f0f0f0;
    border-left: 1px solid #ccc;
    border-radius: 0 8px 8px 0;
  }

  .message {
    margin: 10px 0;
    padding: 10px;
    border-radius: 5px;
    max-width: 70%;
    word-wrap: break-word;
  }

  .message.me {
    background-color: #f0f0f0; /* 浅灰色 */
    align-self: flex-end; /* 靠右对齐 */
    margin-left: auto; /* 使用户消息靠右 */
  }

  .message.API {
    background-color: #e0e0e0; /* 默认系统消息颜色 */
    align-self: flex-start; /* 靠左对齐 */
  }

  .message.system {
    background-color: #f8d7da; /* 错误消息颜色 */
    align-self: flex-start; /* 靠左对齐 */
  }

  .input-area {
    display: flex;
    margin-top: 10px;
    justify-content: flex-end; /* 使输入框和按钮靠右 */
    padding: 10px; /* 为输入区域添加内边距 */
    background-color: #f9f9f9; /* 输入区域背景色 */
  }

  input {
    flex: 1;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 4px;
    margin-right: 5px; /* 右侧留出空间 */
  }

  button {
    padding: 10px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    display: flex;
    align-items: center;
  }

  .send-button {
    background-color: white; /* 默认背景色 */
    color: black; /* 默认文字颜色 */
  }

  .send-button.active {
    background-color: black; /* 有输入时的背景色 */
    color: white; /* 有输入时的文字颜色 */
  }

  .arrow {
    font-size: 20px; /* 适当调整箭头大小 */
  }

  button:hover {
    background-color: gray; /* 悬停时的背景色 */
  }

  .loading-indicator {
    display: inline-block;
    width: 24px;
    height: 24px;
    border: 4px solid rgba(0, 0, 0, 0.1);
    border-left-color: #000;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 10px 0;
  }

  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }
</style>

<div class="chat-container">
  <div class="chat-box">
    <div class="messages">
      {#each messages as message}
        <div class="message {message.user}" role="message">
          {message.text}
        </div>
      {/each}
      {#if loadingMessage}
        <div class="loading-indicator"></div> <!-- 显示加载指示器 -->
      {/if}
    </div>
    <div class="input-area">
      <input bind:value={input} on:keypress={e => e.key === 'Enter' && sendMessage()} placeholder="输入消息..." />
      <button class="send-button {input ? 'active' : ''}" on:click={sendMessage}>
        <span class="arrow">↑</span> <!-- 向上箭头 -->
      </button>
    </div>
  </div>
  <div class="right-panel">
    <RightPanel />
  </div>
</div>

<!--这块代码有个问题，就是系统还没有返回消息时，就显示出了消息框的灰底。-->
<!--这样看起来效果不是很好，做个改造，在等待系统消息返回时，不要显示系统消息框的灰底，而是实现一个类似openai chatgpt那种的小圈圈，让用户知道在等待系统响应。-->
<!--<script>-->
<!--  import { httpRequest } from './HttpRequest.svelte';-->
<!--  import { selectedMode, selectedConnector, selectedDataset } from '../js/store.js';-->
<!--  import RightPanel from './RightPanel.svelte';-->

<!--  let messages = [];-->
<!--  let input = '';-->
<!--  let loadingMessage = false; // 加载状态-->

<!--  function sendMessage() {-->
<!--    if (input.trim()) {-->
<!--      const userMessage = { text: input, user: 'me' };-->
<!--      messages = [...messages, userMessage];-->
<!--      input = '';-->
<!--      agentProcess(userMessage.text);-->
<!--    }-->
<!--  }-->

<!--  async function agentProcess(personInput) {-->
<!--    loadingMessage = true; // 开始加载-->
<!--    let body = {-->
<!--      agent_type: $selectedMode,-->
<!--      person_input: personInput-->
<!--    };-->

<!--    if ($selectedMode === "sql") {-->
<!--      body["data_connector_id"] = $selectedConnector;-->
<!--    } else if ($selectedMode === "rag") {-->
<!--      body["dataset_id"] = $selectedDataset;-->
<!--    }-->

<!--    try {-->
<!--      const ret = await httpRequest('/agent/process', 'POST', body);-->
<!--      if (ret.code === 0) {-->
<!--        messages = [...messages, { text: ret.data.answer, user: 'API' }];-->
<!--      }-->
<!--    } catch (error) {-->
<!--      console.error(error);-->
<!--      messages = [...messages, { text: '错误: ' + error.message, user: '系统' }];-->
<!--    } finally {-->
<!--      loadingMessage = false; // 加载完成-->
<!--    }-->

<!--    console.log(messages);-->
<!--  }-->
<!--</script>-->

<!--<style>-->
<!--  .chat-container {-->
<!--    display: flex;-->
<!--    height: 100%;-->
<!--  }-->

<!--  .chat-box {-->
<!--    flex: 0 0 85%; /* 左侧占 85% */-->
<!--    display: flex;-->
<!--    flex-direction: column; /* 垂直布局 */-->
<!--    border: 1px solid #ccc;-->
<!--    border-radius: 8px;-->
<!--    background-color: #f9f9f9;-->
<!--  }-->

<!--  .messages {-->
<!--    flex: 1; /* 消息区域占据剩余空间 */-->
<!--    overflow-y: auto; /* 仅消息区域可滚动 */-->
<!--    padding: 10px;-->
<!--  }-->

<!--  .right-panel {-->
<!--    flex: 0 0 15%; /* 右侧占 15% */-->
<!--    padding: 10px;-->
<!--    background-color: #f0f0f0;-->
<!--    border-left: 1px solid #ccc;-->
<!--    border-radius: 0 8px 8px 0;-->
<!--  }-->

<!--  .message {-->
<!--    margin: 10px 0;-->
<!--    padding: 10px;-->
<!--    border-radius: 5px;-->
<!--    max-width: 70%;-->
<!--    word-wrap: break-word;-->
<!--  }-->

<!--  .message.me {-->
<!--    background-color: #f0f0f0; /* 浅灰色 */-->
<!--    align-self: flex-end; /* 靠右对齐 */-->
<!--    margin-left: auto; /* 使用户消息靠右 */-->
<!--  }-->

<!--  .message.API {-->
<!--    background-color: #e0e0e0; /* 默认系统消息颜色 */-->
<!--    align-self: flex-start; /* 靠左对齐 */-->
<!--  }-->

<!--  .message.system {-->
<!--    background-color: #f8d7da; /* 错误消息颜色 */-->
<!--    align-self: flex-start; /* 靠左对齐 */-->
<!--  }-->

<!--  .input-area {-->
<!--    display: flex;-->
<!--    margin-top: 10px;-->
<!--    justify-content: flex-end; /* 使输入框和按钮靠右 */-->
<!--    padding: 10px; /* 为输入区域添加内边距 */-->
<!--    background-color: #f9f9f9; /* 输入区域背景色 */-->
<!--  }-->

<!--  input {-->
<!--    flex: 1;-->
<!--    padding: 10px;-->
<!--    border: 1px solid #ccc;-->
<!--    border-radius: 4px;-->
<!--    margin-right: 5px; /* 右侧留出空间 */-->
<!--  }-->

<!--  button {-->
<!--    padding: 10px;-->
<!--    border: none;-->
<!--    border-radius: 4px;-->
<!--    cursor: pointer;-->
<!--    display: flex;-->
<!--    align-items: center;-->
<!--  }-->

<!--  .send-button {-->
<!--    background-color: white; /* 默认背景色 */-->
<!--    color: black; /* 默认文字颜色 */-->
<!--  }-->

<!--  .send-button.active {-->
<!--    background-color: black; /* 有输入时的背景色 */-->
<!--    color: white; /* 有输入时的文字颜色 */-->
<!--  }-->

<!--  .arrow {-->
<!--    font-size: 20px; /* 适当调整箭头大小 */-->
<!--  }-->

<!--  button:hover {-->
<!--    background-color: gray; /* 悬停时的背景色 */-->
<!--  }-->

<!--  .skeleton {-->
<!--    background-color: #e0e0e0;-->
<!--    height: 36px;-->
<!--    border-radius: 4px;-->
<!--    margin: 10px 0;-->
<!--    animation: shimmer 1.5s infinite linear;-->
<!--  }-->

<!--  @keyframes shimmer {-->
<!--    0% {-->
<!--      background-position: -200px 0;-->
<!--    }-->
<!--    100% {-->
<!--      background-position: 200px 0;-->
<!--    }-->
<!--  }-->
<!--</style>-->

<!--<div class="chat-container">-->
<!--  <div class="chat-box">-->
<!--    <div class="messages">-->
<!--      {#each messages as message}-->
<!--        <div class="message {message.user}" role="message">-->
<!--          {message.text}-->
<!--        </div>-->
<!--      {/each}-->
<!--      {#if loadingMessage}-->
<!--        <div class="skeleton"></div>-->
<!--      {/if}-->
<!--    </div>-->
<!--    <div class="input-area">-->
<!--      <input bind:value={input} on:keypress={e => e.key === 'Enter' && sendMessage()} placeholder="输入消息..." />-->
<!--      <button class="send-button {input ? 'active' : ''}" on:click={sendMessage}>-->
<!--        <span class="arrow">↑</span> &lt;!&ndash; 向上箭头 &ndash;&gt;-->
<!--      </button>-->
<!--    </div>-->
<!--  </div>-->
<!--  <div class="right-panel">-->
<!--    <RightPanel />-->
<!--  </div>-->
<!--</div>-->

<!--对这个组件用skeleton进行显示效果优化。-->

<!--<script>-->
<!--  import { httpRequest } from './HttpRequest.svelte';-->
<!--  import { selectedMode, selectedConnector, selectedDataset } from '../js/store.js';-->
<!--  import RightPanel from './RightPanel.svelte';-->

<!--  let messages = [];-->
<!--  let input = '';-->

<!--  function sendMessage() {-->
<!--    if (input.trim()) {-->
<!--      const userMessage = { text: input, user: 'me' };-->
<!--      messages = [...messages, userMessage];-->
<!--      agentProcess(userMessage.text);-->
<!--      input = '';-->
<!--    }-->
<!--  }-->

<!--  async function agentProcess(personInput) {-->
<!--    let body = {-->
<!--      agent_type: $selectedMode,-->
<!--      person_input: personInput-->
<!--    };-->

<!--    if ($selectedMode === "sql") {-->
<!--      body["data_connector_id"] = $selectedConnector;-->
<!--    } else if ($selectedMode === "rag") {-->
<!--      body["dataset_id"] = $selectedDataset;-->
<!--    }-->

<!--    try {-->
<!--      const ret = await httpRequest('/agent/process', 'POST', body);-->
<!--      if (ret.code === 0) {-->
<!--        messages = [...messages, { text: ret.data.answer, user: 'API' }];-->
<!--      }-->
<!--    } catch (error) {-->
<!--      console.error(error);-->
<!--      messages = [...messages, { text: '错误: ' + error.message, user: '系统' }];-->
<!--    }-->

<!--    console.log(messages);-->
<!--  }-->
<!--</script>-->

<!--<style>-->
<!--  .chat-container {-->
<!--    display: flex;-->
<!--    height: 100%;-->
<!--  }-->

<!--  .chat-box {-->
<!--    flex: 0 0 85%; /* 左侧占 85% */-->
<!--    display: flex;-->
<!--    flex-direction: column; /* 垂直布局 */-->
<!--    border: 1px solid #ccc;-->
<!--    border-radius: 8px;-->
<!--    background-color: #f9f9f9;-->
<!--  }-->

<!--  .messages {-->
<!--    flex: 1; /* 消息区域占据剩余空间 */-->
<!--    overflow-y: auto; /* 仅消息区域可滚动 */-->
<!--    padding: 10px;-->
<!--  }-->

<!--  .right-panel {-->
<!--    flex: 0 0 15%; /* 右侧占 15% */-->
<!--    padding: 10px;-->
<!--    background-color: #f0f0f0;-->
<!--    border-left: 1px solid #ccc;-->
<!--    border-radius: 0 8px 8px 0;-->
<!--  }-->

<!--  .message {-->
<!--    margin: 10px 0;-->
<!--    padding: 10px;-->
<!--    border-radius: 5px;-->
<!--    max-width: 70%;-->
<!--    word-wrap: break-word;-->
<!--  }-->

<!--  .message.me {-->
<!--    background-color: #f0f0f0; /* 浅灰色 */-->
<!--    align-self: flex-end; /* 靠右对齐 */-->
<!--    margin-left: auto; /* 使用户消息靠右 */-->
<!--  }-->

<!--  .message.API {-->
<!--    background-color: #e0e0e0; /* 默认系统消息颜色 */-->
<!--    align-self: flex-start; /* 靠左对齐 */-->
<!--  }-->

<!--  .message.system {-->
<!--    background-color: #f8d7da; /* 错误消息颜色 */-->
<!--    align-self: flex-start; /* 靠左对齐 */-->
<!--  }-->

<!--  .input-area {-->
<!--    display: flex;-->
<!--    margin-top: 10px;-->
<!--    justify-content: flex-end; /* 使输入框和按钮靠右 */-->
<!--    padding: 10px; /* 为输入区域添加内边距 */-->
<!--    background-color: #f9f9f9; /* 输入区域背景色 */-->
<!--  }-->

<!--  input {-->
<!--    flex: 1;-->
<!--    padding: 10px;-->
<!--    border: 1px solid #ccc;-->
<!--    border-radius: 4px;-->
<!--    margin-right: 5px; /* 右侧留出空间 */-->
<!--  }-->

<!--  button {-->
<!--    padding: 10px;-->
<!--    border: none;-->
<!--    border-radius: 4px;-->
<!--    cursor: pointer;-->
<!--    display: flex;-->
<!--    align-items: center;-->
<!--  }-->

<!--  .send-button {-->
<!--    background-color: white; /* 默认背景色 */-->
<!--    color: black; /* 默认文字颜色 */-->
<!--  }-->

<!--  .send-button.active {-->
<!--    background-color: black; /* 有输入时的背景色 */-->
<!--    color: white; /* 有输入时的文字颜色 */-->
<!--  }-->

<!--  .arrow {-->
<!--    font-size: 20px; /* 适当调整箭头大小 */-->
<!--  }-->

<!--  button:hover {-->
<!--    background-color: gray; /* 悬停时的背景色 */-->
<!--  }-->
<!--</style>-->

<!--<div class="chat-container">-->
<!--  <div class="chat-box">-->
<!--    <div class="messages">-->
<!--      {#each messages as message}-->
<!--        <div class="message {message.user}" role="message">-->
<!--          {message.text}-->
<!--        </div>-->
<!--      {/each}-->
<!--    </div>-->
<!--    <div class="input-area">-->
<!--      <input bind:value={input} on:keypress={e => e.key === 'Enter' && sendMessage()} placeholder="输入消息..." />-->
<!--      <button class="send-button {input ? 'active' : ''}" on:click={sendMessage}>-->
<!--        <span class="arrow">↑</span> &lt;!&ndash; 向上箭头 &ndash;&gt;-->
<!--      </button>-->
<!--    </div>-->
<!--  </div>-->
<!--  <div class="right-panel">-->
<!--    <RightPanel />-->
<!--  </div>-->
<!--</div>-->
