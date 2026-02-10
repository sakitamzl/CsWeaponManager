using System.Text.Json;
using System.Text.Json.Serialization;
using Microsoft.AspNetCore.Mvc;

var builder = WebApplication.CreateBuilder(args);

// 配置端口
builder.WebHost.ConfigureKestrel(options =>
{
    options.ListenAnyIP(9004);
});

// 添加 CORS 支持
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

// 配置 JSON 序列化
builder.Services.Configure<Microsoft.AspNetCore.Http.Json.JsonOptions>(options =>
{
    options.SerializerOptions.PropertyNamingPolicy = JsonNamingPolicy.CamelCase;
    options.SerializerOptions.WriteIndented = true;
    options.SerializerOptions.DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull;
});

// 添加 Swagger/OpenAPI
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// 添加更新服务
builder.Services.AddSingleton<UpdateService>();

var app = builder.Build();

// 启用 CORS
app.UseCors();

// 配置 Swagger
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

// 启动消息
Console.WriteLine("============================================================");
Console.WriteLine("🚀 CS Weapon Manager - 更新服务器");
Console.WriteLine("============================================================");
Console.WriteLine($"📁 程序目录: {AppContext.BaseDirectory}");
Console.WriteLine($"📁 版本目录: {Path.Combine(AppContext.BaseDirectory, "Releases")}");
Console.WriteLine($"🌐 服务器地址: http://0.0.0.0:9004");
Console.WriteLine("============================================================");
Console.WriteLine("✅ 服务器已启动，版本信息将在每次请求时动态加载");
Console.WriteLine("============================================================\n");

// ============================================
// API 端点
// ============================================

// 健康检查
app.MapGet("/health", () => Results.Ok(new
{
    Success = true,
    Message = "UpdateServer is running",
    Port = 9004,
    Timestamp = DateTime.Now
}))
.WithName("HealthCheck")
.WithOpenApi();

// 检查更新
app.MapGet("/api/update/check", ([FromQuery] string currentVersion, UpdateService service) =>
{
    try
    {
        Console.WriteLine($"📥 收到更新检查请求，客户端版本: {currentVersion}");

        // 每次请求都重新读取版本列表
        var versions = service.GetAvailableVersions();
        Console.WriteLine($"📦 当前可用版本数: {versions.Count}");

        var latest = service.GetLatestVersion();
        if (latest == null)
        {
            Console.WriteLine("⚠️  暂无可用更新版本");
            return Results.Ok(new
            {
                Success = true,
                HasUpdate = false,
                Message = "暂无可用更新版本"
            });
        }

        var hasUpdate = service.CompareVersions(latest.Version, currentVersion) > 0;

        if (!hasUpdate)
        {
            Console.WriteLine($"✅ 客户端已是最新版本 (服务器最新版本: {latest.Version})");
            return Results.Ok(new
            {
                Success = true,
                HasUpdate = false,
                Message = "当前已是最新版本"
            });
        }

        Console.WriteLine($"🆕 发现新版本: {latest.Version}");

        return Results.Ok(new
        {
            Success = true,
            HasUpdate = true,
            Data = new
            {
                CurrentVersion = currentVersion,
                LatestVersion = latest.Version,
                ReleaseDate = latest.ReleaseDate,
                FileSize = latest.FileSizeFormatted,
                Changelog = latest.Changelog,
                Required = latest.Required,
                Description = latest.Description
            }
        });
    }
    catch (Exception ex)
    {
        Console.WriteLine($"❌ 检查更新失败: {ex.Message}");
        return Results.Json(new ApiResponse<object>
        {
            Success = false,
            Error = ex.Message
        }, statusCode: 500);
    }
})
.WithName("CheckUpdate")
.WithOpenApi();

// 下载更新包
app.MapGet("/api/update/download", (UpdateService service) =>
{
    try
    {
        Console.WriteLine("📥 收到更新包下载请求");

        // 每次请求都重新读取版本列表
        var latest = service.GetLatestVersion();
        if (latest == null)
        {
            Console.WriteLine("⚠️  暂无可用更新版本");
            return Results.Json(new ApiResponse<object>
            {
                Success = false,
                Error = "暂无可用更新版本"
            }, statusCode: 404);
        }

        if (!latest.HasPackage || string.IsNullOrEmpty(latest.PackagePath))
        {
            return Results.Json(new ApiResponse<object>
            {
                Success = false,
                Error = "更新包文件不存在"
            }, statusCode: 404);
        }

        if (!File.Exists(latest.PackagePath))
        {
            return Results.Json(new ApiResponse<object>
            {
                Success = false,
                Error = "更新包文件不存在"
            }, statusCode: 404);
        }

        Console.WriteLine($"📤 开始发送更新包: {latest.PackagePath}");
        Console.WriteLine($"📦 文件大小: {latest.FileSizeFormatted}");

        return Results.File(latest.PackagePath, "application/zip", "update.zip");
    }
    catch (Exception ex)
    {
        Console.WriteLine($"❌ 下载更新包失败: {ex.Message}");
        return Results.Json(new ApiResponse<object>
        {
            Success = false,
            Error = ex.Message
        }, statusCode: 500);
    }
})
.WithName("DownloadUpdate")
.WithOpenApi();

// 列出所有版本
app.MapGet("/api/update/versions", (UpdateService service) =>
{
    try
    {
        var versions = service.GetAvailableVersions();
        return Results.Ok(new ApiResponse<List<VersionInfo>>
        {
            Success = true,
            Data = versions
        });
    }
    catch (Exception ex)
    {
        Console.WriteLine($"❌ 获取版本列表失败: {ex.Message}");
        return Results.Json(new ApiResponse<object>
        {
            Success = false,
            Error = ex.Message
        }, statusCode: 500);
    }
})
.WithName("ListVersions")
.WithOpenApi();

app.Run();

// ============================================
// 数据模型
// ============================================

public class ApiResponse<T>
{
    public bool Success { get; set; }
    public T? Data { get; set; }
    public string? Error { get; set; }
    public string? Message { get; set; }
}

public class VersionInfo
{
    public string Version { get; set; } = string.Empty;
    public string ReleaseDate { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public bool Required { get; set; }
    public List<string> Changelog { get; set; } = new();
    public bool HasPackage { get; set; }
    public string? PackagePath { get; set; }
    public long FileSize { get; set; }

    [JsonIgnore]
    public string FileSizeFormatted => FormatFileSize(FileSize);

    private static string FormatFileSize(long bytes)
    {
        string[] sizes = { "B", "KB", "MB", "GB", "TB" };
        double len = bytes;
        int order = 0;
        while (len >= 1024 && order < sizes.Length - 1)
        {
            order++;
            len /= 1024;
        }
        return $"{len:0.#} {sizes[order]}";
    }
}

public class VersionMetadata
{
    public string Version { get; set; } = string.Empty;

    [JsonPropertyName("release_date")]
    public string ReleaseDate { get; set; } = string.Empty;

    public string Description { get; set; } = string.Empty;
    public bool Required { get; set; }
    public List<string> Changelog { get; set; } = new();
}

// ============================================
// 更新服务
// ============================================

public class UpdateService
{
    private const string ReleasesDir = "Releases";
    private readonly string _releasesPath;

    public UpdateService()
    {
        _releasesPath = Path.Combine(AppContext.BaseDirectory, ReleasesDir);

        // 确保 Releases 目录存在（但不强制要求有内容）
        if (!Directory.Exists(_releasesPath))
        {
            try
            {
                Directory.CreateDirectory(_releasesPath);
                Console.WriteLine($"📁 已创建 Releases 目录: {_releasesPath}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"⚠️  无法创建 Releases 目录: {ex.Message}");
            }
        }
    }

    public List<VersionInfo> GetAvailableVersions()
    {
        var versions = new List<VersionInfo>();

        if (!Directory.Exists(_releasesPath))
        {
            Console.WriteLine($"📁 Releases 目录不存在: {_releasesPath}");
            return versions;
        }

        var dirs = Directory.GetDirectories(_releasesPath);
        Console.WriteLine($"📂 扫描 Releases 目录，找到 {dirs.Length} 个子目录");

        foreach (var dir in dirs)
        {
            var dirName = Path.GetFileName(dir);

            // 检查目录名是否符合 vX.Y.Z 格式
            if (!System.Text.RegularExpressions.Regex.IsMatch(dirName, @"^v\d+\.\d+\.\d+$",
                System.Text.RegularExpressions.RegexOptions.IgnoreCase))
            {
                Console.WriteLine($"  ⏭️  跳过非版本目录: {dirName}");
                continue;
            }

            Console.WriteLine($"  📦 检测到版本: {dirName}");

            var versionInfo = new VersionInfo
            {
                Version = dirName
            };

            // 读取 version.json
            var jsonPath = Path.Combine(dir, "version.json");
            if (File.Exists(jsonPath))
            {
                try
                {
                    var json = File.ReadAllText(jsonPath);
                    var metadata = JsonSerializer.Deserialize<VersionMetadata>(json);
                    if (metadata != null)
                    {
                        versionInfo.ReleaseDate = metadata.ReleaseDate;
                        versionInfo.Description = metadata.Description;
                        versionInfo.Required = metadata.Required;
                        versionInfo.Changelog = metadata.Changelog;
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"⚠️  读取版本信息失败: {jsonPath}, 错误: {ex.Message}");
                }
            }

            // 检查更新包
            var packagePath = Path.Combine(dir, "update.zip");
            if (File.Exists(packagePath))
            {
                versionInfo.HasPackage = true;
                versionInfo.PackagePath = packagePath;
                versionInfo.FileSize = new FileInfo(packagePath).Length;
                Console.WriteLine($"     ✅ 找到更新包: update.zip ({versionInfo.FileSizeFormatted})");
            }
            else
            {
                Console.WriteLine($"     ⚠️  缺少更新包: update.zip");
            }

            versions.Add(versionInfo);
        }

        Console.WriteLine($"📊 共加载 {versions.Count} 个版本，其中 {versions.Count(v => v.HasPackage)} 个包含更新包");

        // 按版本号排序（从新到旧）
        versions.Sort((a, b) => CompareVersions(b.Version, a.Version));

        return versions;
    }

    public VersionInfo? GetLatestVersion()
    {
        var versions = GetAvailableVersions();
        return versions.FirstOrDefault(v => v.HasPackage);
    }

    public int CompareVersions(string v1, string v2)
    {
        try
        {
            var version1 = ParseVersion(v1);
            var version2 = ParseVersion(v2);

            return version1.CompareTo(version2);
        }
        catch
        {
            return 0;
        }
    }

    private Version ParseVersion(string versionStr)
    {
        // 移除 'v' 前缀
        versionStr = versionStr.TrimStart('v', 'V');
        return Version.Parse(versionStr);
    }
}
