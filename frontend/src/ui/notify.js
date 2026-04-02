import { reactive } from 'vue';

export const notifyState = reactive({
  items: []
});

let _id = 1;

function push({ variant = 'info', message = '', duration = 2000 } = {}) {
  const id = _id++;
  notifyState.items.push({ id, variant, message, duration });

  window.setTimeout(() => {
    const i = notifyState.items.findIndex(x => x.id === id);
    if (i !== -1) notifyState.items.splice(i, 1);
  }, duration);

  return id;
}

export const notify = {
  success(message, opts = {}) { return push({ variant: 'success', message, ...opts }); },
  error(message, opts = {}) { return push({ variant: 'danger', message, ...opts }); },
  info(message, opts = {}) { return push({ variant: 'info', message, ...opts }); },
  warn(message, opts = {}) { return push({ variant: 'warning', message, ...opts }); },
};