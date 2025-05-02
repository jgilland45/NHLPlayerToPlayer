<template>
  <div v-if="notLoggedIn">
    <input
      v-model="loginModel"
      @keyup.enter="submitUsername"
    />
  </div>
  <div
    v-else
    class="main_page_container"
  >
    <RouterLink
      class="link_button"
      to="/singleplayer"
    >
      Single Player Game
    </RouterLink>
    <RouterLink
      class="link_button"
      to="/multiplayer"
    >
      Multi Player Game
    </RouterLink>
    <h1>WebSocket Chat</h1>
    <form action="" :onsubmit="sendMessage">
        <input v-model="inputText" type="text" id="messageText" autocomplete="off"/>
        <button>Send</button>
    </form>
    <div id='messages'>
      <div v-for="message in messages">
        {{ message }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useUserStore } from '@/stores/user';

const { setUserName } = useUserStore();

const notLoggedIn = ref<boolean>(true);
const loginModel = ref<string>('');
const messages = ref<string[]>([]);
const inputText = ref<string>('');

var ws: WebSocket | null = null;

const sendMessage = () => {
  if (ws) {
    ws.send(inputText.value);
    inputText.value = '';
  }
};

const submitUsername = () => {
  setUserName(loginModel.value);
  notLoggedIn.value = false;
  ws = new WebSocket(`ws://localhost:8080/ws/hi`);  
  ws.onmessage = function(event) {
    messages.value.push(event.data);
  };
};
</script>

<style lang="postcss" scoped>
.main_page_container {
  @apply flex flex-col justify-center items-center p-10 text-white;
}
</style>
