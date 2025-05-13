# 交通事故数据分析系统

## 数据准备

### 第一步：准备数据文件

1. 在项目根目录下创建 `data/output` 文件夹
2. 在 `data/output` 下创建子文件夹，例如，文件夹的名字无所谓，只要目录格式正确即可：
   ```
   data/output/
   ├── 2024.7.1/
   ├── 2024.6.1/
   ├── 2024.5.2/
   ├── 2024.5.1/
   ├── 2024.4.3/
   ├── 2024.2.2/
   └── 2024.2.1/
   ```

3. 找到 `using_ollama_as_llm.py`，运行之后，`data/output` 路径下会生成 `accidents.txt`，请检查是否正确生成。

4. 运行 `using_ollama_as_llm.py`，如果遇到问题：
   - 如果出现 `ModuleNotFoundError: No module named 'tenacity'`，请运行：
     ```bash
     pip install tenacity
     ```
   - 如果出现其他模块缺失错误，请使用 pip 安装相应模块

5. 运行成功标志：
   - 如果看到类似下图的输出，说明程序正在运行中，请耐心等待结果：
   ![运行成功标志](https://github.com/user-attachments/assets/3d420415-0934-4022-bbcb-9aa0e9e1258d)
