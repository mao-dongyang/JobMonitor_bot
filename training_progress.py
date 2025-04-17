# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "matplotlib",
#     "pyyaml",
#     "requests",
# ]
# ///
import requests
import yaml
import time
import matplotlib.pyplot as plt

# === Load Configuration ===
def load_config(path='config.yaml'):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

# === Send Message ===
def send_message(token, chat_id, text, parse_mode='Markdown'):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {'chat_id': chat_id, 'text': text, 'parse_mode': parse_mode}
    resp = requests.post(url, data=data).json()
    return resp['result']['message_id']

# === Update Message ===
def update_message(token, chat_id, message_id, text, parse_mode='Markdown'):
    url = f"https://api.telegram.org/bot{token}/editMessageText"
    data = {
        'chat_id': chat_id,
        'message_id': message_id,
        'text': text,
        'parse_mode': parse_mode
    }
    requests.post(url, data=data)

# === Build Progress Bar ===
def build_progress_bar(current, total, length=20):
    percent = current / total
    filled = int(length * percent)
    return f"[{'█'*filled}{'░'*(length-filled)}] {int(percent*100)}%"

# === Plot Loss Curve ===
def plot_loss_curve(loss_list, path='loss_plot.png'):
    plt.figure()
    plt.plot(loss_list, label='Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Training Loss Curve')
    plt.legend()
    plt.grid(True)
    plt.savefig(path)
    plt.close()

# === Send File ===
def send_file(token, chat_id, file_path, file_type='document', caption=None):
    url = f"https://api.telegram.org/bot{token}/send{file_type.capitalize()}"
    with open(file_path, 'rb') as f:
        files = {file_type: f}
        data = {'chat_id': chat_id}
        if caption:
            data['caption'] = caption
        requests.post(url, data=data, files=files)

# === Write Log ===
def write_log(epoch, loss, log_path='train.log'):
    with open(log_path, 'a') as f:
        f.write(f"Epoch {epoch}: Loss = {loss:.4f}\n")

# === Main Program ===
config = load_config()
token = config['telegram']['token']
chat_id = config['telegram']['chat_id']

# Simulate training parameters
total_epochs = 10
loss_list = []

# 1. Start Notification
start_time = time.time()
msg_id = send_message(token, chat_id, "🟢 *Training Started*\nInitializing training...")

# 2. Simulate Training Process + Real-time Update + Logging
with open('train.log', 'w') as log_file:  # Clear the file first
    log_file.write("Training started...\n")
    for epoch in range(1, total_epochs + 1):
        loss = 1.0 / epoch  # Assume loss
        loss_list.append(loss)

        # Write to training log file
        write_log(epoch, loss)

        # Update progress bar
        bar = build_progress_bar(epoch, total_epochs)
        update_text = (
            f"🔄 *Training Progress*\n"
            f"{bar}\n"
            f"Epoch: {epoch} / {total_epochs}\n"
            f"Loss: `{loss:.4f}`"
        )
        update_message(token, chat_id, msg_id, update_text)
        time.sleep(1.2)

# 3. Training Complete
end_time = time.time()
elapsed = end_time - start_time
elapsed_str = f"{int(elapsed)}s" if elapsed < 60 else f"{elapsed/60:.1f} min"
send_message(token, chat_id, f"✅ *Training Complete!*\n🕒 Time taken: `{elapsed_str}`")

# 4. Generate Loss Curve Plot
plot_loss_curve(loss_list)

# 5. Send Log and Loss Plot
send_file(token, chat_id, 'loss_plot.png', file_type='photo', caption="📈 Loss Curve")
send_file(token, chat_id, 'train.log', file_type='document', caption="📄 Training Log")
