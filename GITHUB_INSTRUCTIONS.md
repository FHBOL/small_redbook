# 推送到GitHub的步骤

1. 在GitHub上创建一个新的仓库（例如，命名为`small_redbook`）

2. 获取仓库的HTTPS或SSH URL，例如：
   HTTPS: https://github.com/yourusername/small_redbook.git
   SSH: git@github.com:yourusername/small_redbook.git

3. 添加远程仓库：
   ```bash
   git remote add origin <仓库URL>
   ```

4. 推送代码到GitHub：
   ```bash
   git push -u origin master
   ```

这样就将代码推送到GitHub了。