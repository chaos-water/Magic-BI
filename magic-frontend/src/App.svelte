<script>
  import Router from 'svelte-spa-router';
  import Sidebar from './components/Sidebar.svelte';
  import Chat from './components/Chat.svelte';

  // 引入其他页面组件
  import FileManagement from './components/FileManagement.svelte';
  import DataConnector from './components/DataConnector.svelte';
  import BusinessSystem from './components/BusinessSystem.svelte';

  const routes = {
    '/chat': Chat,
    '/file-management': FileManagement,
    '/data-connector': DataConnector,
    '/business-system': BusinessSystem,
  };

  let loading = false; // 加载状态
</script>

<style>
  .container {
    display: flex;
    width: 99%;
    height: 97vh;
  }
  .sidebar {
    width: 10%;
    background: #f0f0f0;
  }
  .chat {
    width: 90%;
    background: #fff;
    position: relative; /* 使加载指示器绝对定位 */
  }
  .skeleton {
    height: 100%;
    width: 100%;
    background-color: #e0e0e0;
    border-radius: 8px;
    animation: shimmer 1.5s infinite linear;
    position: absolute;
    top: 0;
    left: 0;
    z-index: 1; /* 确保位于内容上方 */
  }
  @keyframes shimmer {
    0% {
      background-position: -200px 0;
    }
    100% {
      background-position: 200px 0;
    }
  }
</style>

<div class="container">
  <div class="sidebar">
    <Sidebar />
  </div>
  <div class="chat">
    {#if loading}
      <div class="skeleton"></div> <!-- 显示加载占位符 -->
    {/if}
    <Router {routes} on:routeChange={() => loading = true} on:routeChanged={() => loading = false} />
  </div>
</div>

<!--采用skeleton对这个组件进行显示效果优化，要考虑到这个组件引用了其它组件，不要影响引用后的显示效果。-->

<!--<script>-->
<!--  import Router from 'svelte-spa-router';-->
<!--  import Sidebar from './components/Sidebar.svelte';-->
<!--  import Chat from './components/Chat.svelte';-->

<!--  // 引入其他页面组件-->
<!--  import FileManagement from './components/FileManagement.svelte';-->
<!--  import DataConnector from './components/DataConnector.svelte';-->
<!--  import BusinessSystem from './components/BusinessSystem.svelte';-->

<!--  const routes = {-->
<!--    // Exact path-->
<!--    '/chat': Chat,-->

<!--    // Using named parameters, with last being optional-->
<!--    '/file-management': FileManagement,-->

<!--    // Wildcard parameter-->
<!--    '/data-connector': DataConnector,-->

<!--    // Catch-all-->
<!--    // This is optional, but if present it must be the last-->
<!--    '/business-system': BusinessSystem,-->
<!--}-->
<!--</script>-->

<!--<style>-->
<!--  .container {-->
<!--    display: flex;-->
<!--    width: 99%;-->
<!--    height: 97vh;-->
<!--  }-->
<!--  .sidebar {-->
<!--    width: 10%;-->
<!--    background: #f0f0f0;-->
<!--  }-->
<!--  .chat {-->
<!--    width: 90%;-->
<!--    background: #fff;-->
<!--  }-->
<!--</style>-->

<!--<div class="container">-->
<!--  <div class="sidebar">-->
<!--    <Sidebar />-->
<!--  </div>-->
<!--  <div class="chat">-->
<!--    <Router {routes}/>-->
<!--  </div>-->
<!--</div>-->
