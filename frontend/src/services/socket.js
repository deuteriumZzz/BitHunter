import io from 'socket.io-client';

const socket = io('ws://localhost:8000', {
  auth: {
    token: localStorage.getItem('token'),
  },
});

export { socket };
