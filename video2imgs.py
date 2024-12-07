import cv2  
import os
import glob  
  
def split_video_to_images(video_path, output_folder, time_interval=1):
    '''
    Args:
        video_path: 视频路径
        output_folder: 拆分成图片后保存文件夹路径
        time_interval: 时间间隔, 单位秒, 每隔time_interval秒提取一张
    '''  
    # 确保输出文件夹存在  
    if not os.path.exists(output_folder):  
        os.makedirs(output_folder)  
  
    # 打开视频文件  
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if time_interval <= 0:
        frame_interval = 1
    else:
        frame_interval = int(time_interval * fps)
  
    # 检查视频是否成功打开  
    if not cap.isOpened():  
        print("Error opening {}".format(video_path))  
        return  
  
    # 用于计数的变量  
    frame_count = 0  
  
    # 循环读取视频的每一帧  
    while True:  
        # 读取一帧  
        ret, frame = cap.read()  
  
        # 如果读取失败（例如，已经到达视频的末尾），则退出循环  
        if not ret:  
            break  
  
        # 检查是否达到保存帧的间隔  
        if frame_count % frame_interval == 0:  
            # 格式化帧计数器以用于文件名  
            filename = f"frame_{frame_count//frame_interval}.jpg"  
            # 构建完整的文件路径  
            file_path = os.path.join(output_folder, filename)  
  
            # 保存帧为图像文件  
            cv2.imwrite(file_path, frame)  
  
            # 打印保存的图像文件名  
            print(f"Saved {file_path}")  
  
        # 更新帧计数器  
        frame_count += 1  
  
    # 释放视频对象  
    cap.release()  
    print("Video frames saved successfully.")


def batch_video2images(video_dir, save_dir, time_interval):
    os.makedirs(save_dir, exist_ok=True)
    for video_path in glob.glob(os.path.join(video_dir, "*.mp4")):
        name = os.path.splitext(os.path.split(video_path)[-1])[0]
        output_folder = os.path.join(save_dir, name)
        split_video_to_images(video_path, output_folder, time_interval=time_interval)


if __name__=="__main__":
    # 使用函数拆分视频  
    video_file = 'D:/dataset/ceshishuju1203/起重作业警戒线识别.mp4'  # 替换为你的视频文件路径  
    output_dir = 'output_images'        # 替换为你希望保存图像的文件夹  
    split_video_to_images(video_file, output_dir, time_interval=1)  # 每隔1s保存一帧
