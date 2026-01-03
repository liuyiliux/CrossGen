# 项目仓库信息

本文件用于记录项目的两个远程仓库信息，以及如何实现两个仓库的同步更新。

## 📋 仓库列表

| 仓库名称 | 远程别名 | 仓库地址 | 用途 |
|----------|----------|----------|------|
| cnb仓库 | cnb | https://cnb.cool/yiliu/yiliu | 主要开发仓库 |
| GitHub仓库 | github | https://github.com/liuyiliux/CrossGen | 备份和开源分享仓库 |

## 🚀 同步方法

### 方法一：分别推送到两个仓库

1. 提交代码到本地仓库：
   ```bash
   git add .
   git commit -m "你的提交信息"
   ```

2. 推送到cnb仓库：
   ```bash
   git push cnb master
   ```

3. 推送到GitHub仓库：
   ```bash
   git push github master
   ```

### 方法二：一次性推送到所有仓库

1. 添加两个远程仓库（如果尚未添加）：
   ```bash
   git remote add cnb https://cnb.cool/yiliu/yiliu
   git remote add github https://github.com/liuyiliux/CrossGen
   ```

2. 使用`git push --all`命令一次性推送到所有仓库：
   ```bash
   git push --all
   ```

### 方法三：配置多个pushurl（推荐）

1. 查看当前远程仓库配置：
   ```bash
   git remote -v
   ```

2. 为cnb远程仓库添加GitHub的pushurl：
   ```bash
   git remote set-url --add --push cnb https://github.com/liuyiliux/CrossGen
   ```

3. 查看更新后的配置：
   ```bash
   git remote -v
   ```

4. 推送代码到两个仓库：
   ```bash
   git push cnb master
   ```

## 🛠️ 操作指南

### 添加远程仓库

```bash
# 添加cnb仓库
git remote add cnb https://cnb.cool/yiliu/yiliu

# 添加GitHub仓库
git remote add github https://github.com/liuyiliux/CrossGen
```

### 查看远程仓库

```bash
git remote -v
```

### 删除远程仓库

```bash
# 删除cnb仓库
git remote remove cnb

# 删除GitHub仓库
git remote remove github
```

### 查看远程仓库详情

```bash
git remote show cnb
```

## ⚠️ 注意事项

1. **保持同步**：确保两个仓库的代码始终保持同步，避免出现版本差异
2. **优先推送**：建议先推送到cnb仓库，再推送到GitHub仓库
3. **定期检查**：定期检查两个仓库的代码是否一致
4. **避免冲突**：如果两个仓库出现冲突，先解决冲突再推送
5. **保护分支**：建议为master分支设置保护规则，防止意外推送

## 📁 相关文件

- `.git/config`：Git配置文件，包含远程仓库信息
- `README.md`：项目说明文档，包含GitHub地址

## 📞 联系方式

如果在仓库同步过程中遇到问题，请联系：
- 邮箱：44165547@qq.com
- 微信：liuyiliux 说明来意

---

**最后更新时间**：2026-01-03
**版本**：1.0.0