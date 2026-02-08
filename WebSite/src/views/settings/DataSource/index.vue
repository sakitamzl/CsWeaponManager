<template>
  <div>
    <div class="data-source-container">
      <div class="data-sources-list" :class="{ collapsed: isListCollapsed }">
        <!-- 空状态提示 -->
        <div v-if="dataSources.length === 0" class="card">
          <div class="empty-state">
            <el-empty description="暂无数据源">
              <div class="empty-actions">
                <el-button type="primary" @click="openAddDialogForNewSteam" size="large">
                  <el-icon :size="20" style="margin-right: 8px;"><Plus /></el-icon>
                  创建第一个数据源
                </el-button>
              </div>
            </el-empty>
          </div>
        </div>

        <!-- 按SteamID分组显示（有数据时） - 每个分组独立的BOX -->
        <template v-else>
          <!-- SteamID分组数据源 -->
          <div v-for="(group, steamID) in groupedDataSources" :key="steamID" class="steam-group-box">
            <div class="card">
              <div class="steam-group-header">
                <div class="steam-group-header-left">
                  <h4>
                    <el-icon><User /></el-icon>
                    SteamID: {{ steamID === '未设置' ? '未设置' : steamID }}
                    <el-tag size="small" type="info" style="margin-left: 10px;">{{ group.length }} 个数据源</el-tag>
                  </h4>
                </div>
                <div class="steam-group-header-right">
                  <div class="add-source-button" @click="openAddDialog(steamID)">
                    <el-icon :size="20"><Plus /></el-icon>
                    <span>添加数据源</span>
                  </div>
                </div>
              </div>
              <div class="grid grid-datasource">
                <!-- 现有数据源卡片 -->
                <div 
                  v-for="source in group" 
                  :key="source.dataID" 
                  class="source-card"
                >
                  <div class="source-header">
                    <div class="source-info">
                      <h4>{{ source.dataName }}</h4>
                      <el-tag :type="getSourceTypeColor(source.enabled)">{{ getSourceTypeLabel(source.type) }}</el-tag>
                    </div>
                  </div>
                  
                  
                  <div class="source-actions">
                    <el-button type="primary" size="small" @click="editSource(source)">
                      编辑
                    </el-button>
                    <el-button 
                      v-if="source.type !== 'perfectworld'"
                      type="warning" 
                      size="small" 
                      @click="startCollection(source)" 
                      :loading="collectingSourceIds.has(source.dataID)"
                    >
                      {{ collectingSourceIds.has(source.dataID) ? '采集中...' : '采集' }}
                    </el-button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 独立数据源区域 - 置于底部 -->
          <div v-if="independentDataSources.length > 0" class="steam-group-box">
            <div class="card">
              <div class="steam-group-header">
                <div class="steam-group-header-left">
                  <h4>
                    <el-icon><DataAnalysis /></el-icon>
                    独立数据源
                    <el-tag size="small" type="success" style="margin-left: 10px;">{{ independentDataSources.length }} 个数据源</el-tag>
                  </h4>
                </div>
                <div class="steam-group-header-right">
                  <div class="add-source-button" @click="openAddIndependentDataSource">
                    <el-icon :size="20"><Plus /></el-icon>
                    <span>添加独立数据源</span>
                  </div>
                </div>
              </div>
              <div class="grid grid-datasource">
                <!-- 独立数据源卡片 - 只显示编辑按钮 -->
                <div 
                  v-for="source in independentDataSources" 
                  :key="source.dataID" 
                  class="source-card"
                >
                  <div class="source-header">
                    <div class="source-info">
                      <h4>{{ source.dataName }}</h4>
                      <el-tag :type="getSourceTypeColor(source.enabled)">{{ getSourceTypeLabel(source.type) }}</el-tag>
                    </div>
                  </div>
                  
                  <div class="source-actions">
                    <el-button type="primary" size="small" @click="editSource(source)">
                      编辑
                    </el-button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>

      <!-- 新建SteamID分组区域 -->
      <div class="additional-box">
        <div class="card new-steam-group-card" @click="openAddDialogForNewSteam">
          <el-icon :size="32"><Plus /></el-icon>
          <span>新建SteamID分组</span>
        </div>
        <div class="card new-steam-group-card" @click="openAddIndependentDataSource">
          <el-icon :size="32"><Plus /></el-icon>
          <span>添加独立数据源</span>
        </div>
      </div>

    </div>

    <!-- 编辑数据源对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑数据源"
      width="600px"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      @close="handleEditDialogClose"
    >
      <el-form :model="editForm" label-width="120px" ref="editFormRef">
        <el-form-item label="数据源名称" required>
          <el-input 
            v-model="editForm.name" 
            placeholder="请输入数据源名称"
          />
        </el-form-item>
        <el-form-item label="数据源类型">
          <el-select v-model="editForm.type" placeholder="选择数据源类型" style="width: 100%;" disabled>
            <el-option label="Steam市场" value="steam" />
            <el-option label="Steam市场(登录)" value="steam_login" />
            <el-option label="完美世界APP" value="perfectworld" />
            <el-option label="网易BUFF" value="buff" />
            <el-option label="悠悠有品" value="youpin" />
            <el-option label="CsFloat" value="csfloat" />
            <el-option label="CSQAQ" value="csqaq" />
          </el-select>
        </el-form-item>

        <!-- 悠悠有品特有配置 -->
        <YoupinForm
          v-if="editForm.type === 'youpin'"
          ref="youpinFormRef"
          :form="editForm"
          :is-edit-mode="true"
          :proxy-address="proxyAddress"
          @update:form="Object.assign(editForm, $event)"
          @update:proxyAddress="proxyAddress = $event"
          @token-success="handleEditSubmit"
        />

        <!-- BUFF特有配置 -->
        <BuffForm
          v-else-if="editForm.type === 'buff'"
          ref="buffFormRef"
          :form="editForm"
          :is-edit-mode="true"
          :proxy-address="proxyAddress"
          @update:form="Object.assign(editForm, $event)"
          @update:proxyAddress="proxyAddress = $event"
          @token-success="handleEditSubmit"
        />

        <!-- Steam特有配置 -->
        <SteamForm
          v-else-if="editForm.type === 'steam' || editForm.type === 'steam_login'"
          :form="editForm"
          :is-edit-mode="true"
          @update:form="Object.assign(editForm, $event)"
          @token-success="handleEditSubmit"
        />

        <!-- 完美世界APP特有配置 -->
        <PerfectWorldForm
          v-else-if="editForm.type === 'perfectworld'"
          ref="perfectWorldFormRef"
          :form="editForm"
          :is-edit-mode="true"
          :proxy-address="proxyAddress"
          @update:form="Object.assign(editForm, $event)"
          @update:proxyAddress="proxyAddress = $event"
          @token-success="handleEditSubmit"
        />

        <!-- CsFloat特有配置 -->
        <CsfloatForm
          v-else-if="editForm.type === 'csfloat'"
          ref="csfloatFormRef"
          :form="editForm"
          :is-edit-mode="true"
          :proxy-address="proxyAddress"
          @update:form="Object.assign(editForm, $event)"
          @update:proxyAddress="proxyAddress = $event"
          @token-success="handleEditSubmit"
        />

        <!-- CSQAQ特有配置 -->
        <CsqaqForm
          v-else-if="editForm.type === 'csqaq'"
          :form="editForm"
          :is-edit-mode="true"
          @update:form="Object.assign(editForm, $event)"
        />

        <!-- SteamDT特有配置 -->
        <SteamdtForm
          v-else-if="editForm.type === 'steamdt'"
          :form="editForm"
          :is-edit-mode="true"
          @update:form="Object.assign(editForm, $event)"
        />

        <!-- 通用配置 -->
        <template v-else>
          <el-form-item label="API地址">
            <el-input v-model="editForm.apiUrl" placeholder="请输入API地址" />
          </el-form-item>
          <el-form-item label="API密钥">
            <el-input 
              v-model="editForm.apiKey" 
              type="textarea"
              :rows="2"
              placeholder="请输入API密钥"
            />
          </el-form-item>
          <el-form-item label="休眠时间(秒)">
            <el-input-number v-model="editForm.sleepTime" :min="1" :max="86400" style="width: 100%;" />
          </el-form-item>
        </template>

        <el-form-item v-if="['youpin', 'buff', 'steam', 'csfloat'].includes(editForm.type)" label="是否自动采集">
          <el-switch v-model="editForm.enabled" />
        </el-form-item>

      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <div class="dialog-footer-left">
            <el-button 
              v-if="editForm.type === 'youpin'" 
              type="warning" 
              @click="handleEditCollectAll"
              :loading="collectingSourceIds.has(editingSourceId)"
            >
              全部采集
            </el-button>
            <el-button 
              v-if="editForm.type === 'buff'" 
              type="warning" 
              @click="handleEditBuffCollectAll"
              :loading="collectingSourceIds.has(editingSourceId)"
            >
              全部获取
            </el-button>
            <el-button 
              v-if="editForm.type === 'steam'" 
              type="warning" 
              @click="handleEditSteamCollectAll"
              :loading="collectingSourceIds.has(editingSourceId)"
            >
              全部采集
            </el-button>
            <el-button 
              v-if="editForm.type === 'csfloat'" 
              type="warning" 
              @click="handleEditCsfloatCollectAll"
              :loading="collectingSourceIds.has(editingSourceId)"
            >
              全部采集
            </el-button>
            <el-button 
              type="danger" 
              @click="handleEditDelete"
            >
              删除数据源
            </el-button>
          </div>
          <div class="dialog-footer-right">
            <el-button @click="editDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="handleEditSubmit" :loading="editSubmitting">
              保存更改
            </el-button>
          </div>
        </div>
      </template>
    </el-dialog>

    <!-- 添加数据源对话框 -->
    <el-dialog
      v-model="addDialogVisible"
      :title="isIndependentDataSourceMode ? '添加独立数据源' : '添加新数据源'"
      width="600px"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      @close="handleAddDialogClose"
    >
      <el-form :model="inputForm" label-width="120px" @submit.prevent="handleSubmit">
        <el-form-item label="数据源名称" required>
          <el-input 
            v-model="inputForm.name" 
            placeholder="请输入数据源名称"
          />
        </el-form-item>
        <el-form-item label="数据源类型" required>
          <el-select v-model="inputForm.type" placeholder="选择数据源类型" style="width: 100%;" :disabled="isIndependentDataSourceMode">
            <el-option 
              v-if="!isIndependentDataSourceMode"
              label="Steam市场" 
              value="steam" 
              :disabled="isTypeDisabled('steam')"
            >
              <span>Steam市场</span>
              <span v-if="isTypeDisabled('steam')" style="color: #909399; font-size: 12px; margin-left: 10px;">(已存在)</span>
            </el-option>
            <el-option 
              v-if="!isIndependentDataSourceMode"
              label="完美世界APP" 
              value="perfectworld" 
              :disabled="isTypeDisabled('perfectworld')"
            >
              <span>完美世界APP</span>
              <span v-if="isTypeDisabled('perfectworld')" style="color: #909399; font-size: 12px; margin-left: 10px;">(已存在)</span>
            </el-option>
            <el-option 
              v-if="!isIndependentDataSourceMode"
              label="网易BUFF" 
              value="buff" 
              :disabled="isTypeDisabled('buff')"
            >
              <span>网易BUFF</span>
              <span v-if="isTypeDisabled('buff')" style="color: #909399; font-size: 12px; margin-left: 10px;">(已存在)</span>
            </el-option>
            <el-option 
              v-if="!isIndependentDataSourceMode"
              label="悠悠有品" 
              value="youpin" 
              :disabled="isTypeDisabled('youpin')"
            >
              <span>悠悠有品</span>
              <span v-if="isTypeDisabled('youpin')" style="color: #909399; font-size: 12px; margin-left: 10px;">(已存在)</span>
            </el-option>
            <el-option 
              v-if="!isIndependentDataSourceMode"
              label="CsFloat" 
              value="csfloat" 
              :disabled="isTypeDisabled('csfloat')"
            >
              <span>CsFloat</span>
              <span v-if="isTypeDisabled('csfloat')" style="color: #909399; font-size: 12px; margin-left: 10px;">(已存在)</span>
            </el-option>
            <el-option 
              v-if="isIndependentDataSourceMode"
              label="CSQAQ" 
              value="csqaq"
              :disabled="isIndependentTypeDisabled('csqaq')"
            >
              <span>CSQAQ</span>
              <span v-if="isIndependentTypeDisabled('csqaq')" style="color: #909399; font-size: 12px; margin-left: 10px;">(已存在)</span>
            </el-option>
            <el-option 
              v-if="isIndependentDataSourceMode"
              label="SteamDT" 
              value="steamdt"
              :disabled="isIndependentTypeDisabled('steamdt')"
            >
              <span>SteamDT</span>
              <span v-if="isIndependentTypeDisabled('steamdt')" style="color: #909399; font-size: 12px; margin-left: 10px;">(已存在)</span>
            </el-option>
          </el-select>
        </el-form-item>
        
        <!-- BUFF特有配置 -->
        <BuffForm
          v-if="inputForm.type === 'buff'"
          ref="buffFormRef"
          :form="inputForm"
          :is-edit-mode="false"
          :proxy-address="proxyAddress"
          @update:form="Object.assign(inputForm, $event)"
          @update:proxyAddress="proxyAddress = $event"
          @token-success="handleSubmit"
        />
        
        <!-- BUFF特有配置 (旧代码保留，待删除) -->
        <template v-if="false && inputForm.type === 'buff'">
          <el-form-item>
            <el-button 
              type="success" 
              @click="startBuffTokenCollection(false)" 
              :loading="buffTokenLoading"
              :disabled="buffTokenStatus === 'success'"
              style="width: 100%;"
            >
              <el-icon style="margin-right: 5px;"><Grid /></el-icon>
              {{ buffTokenLoading ? '正在获取令牌...' : buffTokenStatus === 'success' ? '✓ 令牌已获取' : '一键获取BUFF令牌' }}
            </el-button>
            <div v-if="buffTokenStatus === 'waiting'" style="margin-top: 10px; padding: 10px; background: #fff7e6; border-radius: 4px; border-left: 3px solid #faad14;">
              <div style="color: #faad14; font-weight: 500; margin-bottom: 5px;">
                <el-icon><Loading /></el-icon> 等待手机APP访问...
              </div>
              <div style="color: #666; font-size: 12px;">
                1. 在手机WiFi设置中配置代理: <strong>{{ proxyAddress || '...' }}</strong><br/>
                2. 打开BUFF APP并登录<br/>
                3. 系统将自动获取令牌
              </div>
            </div>
            <div v-if="buffTokenStatus === 'success'" style="margin-top: 10px; padding: 10px; background: #f6ffed; border-radius: 4px; border-left: 3px solid #52c41a;">
              <div style="color: #52c41a; font-weight: 500;">
                <el-icon><CircleCheck /></el-icon> 令牌获取成功!
              </div>
            </div>
          </el-form-item>
          
          <!-- BUFF配置 -->
          <el-collapse v-model="inputBuffCollapse">
            <el-collapse-item title="BUFF配置" name="config">
              <el-form-item label="app-version" required>
                <el-input v-model="inputForm.buffAppVersion" placeholder="请输入app-version" />
              </el-form-item>
              <el-form-item label="app-version-code">
                <el-input v-model="inputForm.buffAppVersionCode" placeholder="请输入app-version-code" />
              </el-form-item>
              <el-form-item label="brand">
                <el-input v-model="inputForm.buffBrand" placeholder="请输入brand" />
              </el-form-item>
              <el-form-item label="build-fingerprint">
                <el-input v-model="inputForm.buffBuildFingerprint" placeholder="请输入build-fingerprint" />
              </el-form-item>
              <el-form-item label="channel">
                <el-input v-model="inputForm.buffChannel" placeholder="请输入channel" />
              </el-form-item>
              <el-form-item label="device-id">
                <el-input v-model="inputForm.buffDeviceId" placeholder="请输入device-id" />
              </el-form-item>
              <el-form-item label="device-id-weak">
                <el-input v-model="inputForm.buffDeviceIdWeak" placeholder="请输入device-id-weak" />
              </el-form-item>
              <el-form-item label="manufacturer">
                <el-input v-model="inputForm.buffManufacturer" placeholder="请输入manufacturer" />
              </el-form-item>
              <el-form-item label="model">
                <el-input v-model="inputForm.buffModel" placeholder="请输入model" />
              </el-form-item>
              <el-form-item label="network">
                <el-input v-model="inputForm.buffNetwork" placeholder="请输入network" />
              </el-form-item>
              <el-form-item label="product">
                <el-input v-model="inputForm.buffProduct" placeholder="请输入product" />
              </el-form-item>
              <el-form-item label="resolution">
                <el-input v-model="inputForm.buffResolution" placeholder="请输入resolution" />
              </el-form-item>
              <el-form-item label="rom">
                <el-input v-model="inputForm.buffRom" placeholder="请输入rom" />
              </el-form-item>
              <el-form-item label="rom-id">
                <el-input v-model="inputForm.buffRomId" placeholder="请输入rom-id" />
              </el-form-item>
              <el-form-item label="screen-density">
                <el-input v-model="inputForm.buffScreenDensity" placeholder="请输入screen-density" />
              </el-form-item>
              <el-form-item label="screen-size">
                <el-input v-model="inputForm.buffScreenSize" placeholder="请输入screen-size" />
              </el-form-item>
              <el-form-item label="seed">
                <el-input v-model="inputForm.buffSeed" placeholder="请输入seed" />
              </el-form-item>
              <el-form-item label="system-type">
                <el-input v-model="inputForm.buffSystemType" placeholder="请输入system-type" />
              </el-form-item>
              <el-form-item label="system-version">
                <el-input v-model="inputForm.buffSystemVersion" placeholder="请输入system-version" />
              </el-form-item>
              <el-form-item label="timestamp">
                <el-input v-model="inputForm.buffTimestamp" placeholder="请输入timestamp" />
              </el-form-item>
              <el-form-item label="timezone">
                <el-input v-model="inputForm.buffTimezone" placeholder="请输入timezone" />
              </el-form-item>
              <el-form-item label="timezone-offset">
                <el-input v-model="inputForm.buffTimezoneOffset" placeholder="请输入timezone-offset" />
              </el-form-item>
              <el-form-item label="timezone-offset-dst">
                <el-input v-model="inputForm.buffTimezoneOffsetDst" placeholder="请输入timezone-offset-dst" />
              </el-form-item>
              <el-form-item label="user-agent">
                <el-input v-model="inputForm.buffUserAgent" placeholder="请输入user-agent" />
              </el-form-item>
              <el-form-item label="locale">
                <el-input v-model="inputForm.buffLocale" placeholder="请输入locale" />
              </el-form-item>
              <el-form-item label="locale-supported">
                <el-input v-model="inputForm.buffLocaleSupported" placeholder="请输入locale-supported" />
              </el-form-item>
              <el-form-item label="devicename">
                <el-input v-model="inputForm.buffDevicename" placeholder="请输入devicename" />
              </el-form-item>
              <el-form-item label="Cookie" required>
                <el-input 
                  v-model="inputForm.cookie" 
                  type="textarea"
                  :rows="3"
                  placeholder="请输入Cookie"
                />
              </el-form-item>
              <el-form-item label="SteamID" required>
                <el-input v-model="inputForm.steamID" placeholder="请输入SteamID" />
              </el-form-item>
              <el-form-item label="更新频率">
                <el-select v-model="inputForm.updateFreq" placeholder="选择更新频率" style="width: 100%;">
                  <el-option label="每15分钟" value="15min" />
                  <el-option label="每小时" value="1hour" />
                  <el-option label="每3小时" value="3hour" />
                  <el-option label="每6小时" value="6hour" />
                  <el-option label="每12小时" value="12hour" />
                  <el-option label="每天" value="daily" />
                </el-select>
              </el-form-item>
            </el-collapse-item>
          </el-collapse>
        </template>
        
        <!-- Steam特有配置 -->
        <SteamForm
          v-else-if="inputForm.type === 'steam' || inputForm.type === 'steam_login'"
          :form="inputForm"
          :is-edit-mode="false"
          @update:form="Object.assign(inputForm, $event)"
          @token-success="handleSubmit"
        />
        
        <!-- Steam特有配置 (旧代码保留，待删除) -->
        <template v-if="false && inputForm.type === 'steam'">
          <!-- Cookie获取方式选择 -->
          <el-form-item label="获取方式" required>
            <el-radio-group v-model="inputForm.steamCookieMethod">
              <el-radio label="qrcode">扫码登录</el-radio>
              <el-radio label="password">账号密码登录</el-radio>
              <el-radio label="manual">手动输入</el-radio>
            </el-radio-group>
          </el-form-item>

          <!-- 扫码登录 -->
          <template v-if="inputForm.steamCookieMethod === 'qrcode'">
            <el-form-item label="登录二维码">
              <div 
                @click="steamQRStatus !== 'success' ? handleGenerateQRCode() : null"
                :style="{
                  textAlign: 'center', 
                  padding: '20px', 
                  background: '#f5f5f5', 
                  borderRadius: '8px',
                  cursor: steamQRStatus === 'success' ? 'default' : 'pointer',
                  transition: 'all 0.3s'
                }"
                @mouseenter="$event.currentTarget.style.background = steamQRStatus === 'success' ? '#f5f5f5' : '#e8e8e8'"
                @mouseleave="$event.currentTarget.style.background = '#f5f5f5'"
              >
                <div v-if="!steamQRCode && !steamQRLoading">
                  <el-icon :size="80" color="#409EFF"><Grid /></el-icon>
                  <p style="color: #409EFF; margin-top: 10px; font-weight: 500;">点击获取Steam登录二维码</p>
                </div>
                <div v-else-if="steamQRLoading">
                  <el-icon :size="80" class="is-loading" color="#409EFF"><Loading /></el-icon>
                  <p style="color: #409EFF; margin-top: 10px;">正在获取二维码...</p>
                </div>
                <div v-else>
                  <img :src="steamQRCode" alt="Steam登录二维码" style="width: 200px; height: 200px;" />
                  <p style="color: #666; margin-top: 10px; font-size: 14px;">
                    请使用Steam手机APP扫描二维码
                  </p>
                  <el-tag :type="steamQRStatus === 'waiting' ? 'info' : steamQRStatus === 'success' ? 'success' : 'warning'" style="margin-top: 10px;">
                    {{ getSteamQRStatusText() }}
                  </el-tag>
                  <div v-if="steamQRStatus === 'expired'" style="margin-top: 10px;">
                    <el-link type="primary" :underline="false" @click.stop="handleGenerateQRCode">
                      点击刷新二维码
                    </el-link>
                  </div>
                </div>
              </div>
            </el-form-item>
          </template>

          <!-- 账号密码登录 -->
          <template v-else-if="inputForm.steamCookieMethod === 'password'">
            <el-form-item label="Steam用户名" required>
              <el-input 
                v-model="inputForm.steamUsername" 
                placeholder="请输入Steam用户名"
              />
            </el-form-item>
            <el-form-item label="Steam密码" required>
              <el-input 
                v-model="inputForm.steamPassword" 
                type="password"
                show-password
                placeholder="请输入Steam密码"
              />
            </el-form-item>
            <el-form-item label="Steam PIN">
              <el-input 
                v-model="inputForm.steamTwofactorCode" 
                placeholder="请输入5位Steam Guard验证码（如需要）"
                maxlength="5"
              />
              <div style="color: #999; font-size: 12px; margin-top: 5px;">
                如果您的账号启用了Steam Guard手机令牌，请在此输入验证码
              </div>
            </el-form-item>
            <el-form-item>
              <el-button 
                type="success" 
                @click="handleSteamLogin" 
                :loading="steamLoginLoading"
                style="width: 100%;"
              >
                {{ steamLoginLoading ? '登录中...' : '立即登录获取Cookie' }}
              </el-button>
            </el-form-item>
            <!-- 自动获取的 SteamID 显示 -->
            <el-form-item v-if="inputForm.steamID" label="当前SteamID">
              <el-input v-model="inputForm.steamID" disabled />
            </el-form-item>
          </template>

          <!-- 手动输入Cookie -->
          <template v-else-if="inputForm.steamCookieMethod === 'manual'">
          </template>

          <!-- 登录状态提示 -->
          <el-alert
            v-if="inputForm.steamLoginMessage"
            :title="inputForm.steamLoginMessage"
            :type="inputForm.steamLoginSuccess ? 'success' : 'warning'"
            :closable="false"
            show-icon
            style="margin-top: 10px;"
          />

          <!-- Steam配置 -->
          <el-collapse v-model="inputSteamCollapse" style="margin-top: 20px;">
            <el-collapse-item title="Steam配置" name="config">
              <el-form-item label="SteamID" required>
                <el-input 
                  v-model="inputForm.steamID" 
                  placeholder="请输入SteamID"
                />
              </el-form-item>

              <el-form-item label="基础Cookies">
                <el-input
                  v-model="inputForm.steamBaseCookies"
                  type="textarea"
                  :rows="3"
                  placeholder="扫码登录成功后将自动填入，可手动粘贴基础Cookie"
                />
                <div style="color: #999; font-size: 12px; margin-top: 4px;">
                  基础Cookies为扫码后立即返回的原始Cookie，建议同时保存以备验证。
                </div>
              </el-form-item>
              <el-form-item label="库存Cookies" required>
                <el-input
                  v-model="inputForm.steamInventoryCookies"
                  type="textarea"
                  :rows="3"
                  placeholder="访问库存页后的完整Cookie，采集库存时将使用该值"
                />
                <div style="color: #999; font-size: 12px; margin-top: 4px;">
                  若使用手动方式，请先填写基础Cookies，再填写库存Cookies。
                </div>
              </el-form-item>
            </el-collapse-item>
          </el-collapse>
        </template>

        <!-- Steam登录特有配置（已废弃，保留兼容） -->
        <template v-else-if="inputForm.type === 'steam_login'">
          <!-- 登录方式选择 -->
          <el-form-item label="登录方式" required>
            <el-radio-group v-model="inputForm.steamLoginMethod">
              <el-radio label="qrcode">扫码登录（推荐）</el-radio>
              <el-radio label="password">账号密码登录</el-radio>
            </el-radio-group>
          </el-form-item>

          <!-- 扫码登录 -->
          <template v-if="inputForm.steamLoginMethod === 'qrcode'">
            <el-form-item label="登录二维码">
              <div 
                @click="steamQRStatus !== 'success' ? handleGenerateQRCode() : null"
                :style="{
                  textAlign: 'center', 
                  padding: '20px', 
                  background: '#f5f5f5', 
                  borderRadius: '8px',
                  cursor: steamQRStatus === 'success' ? 'default' : 'pointer',
                  transition: 'all 0.3s'
                }"
                @mouseenter="$event.currentTarget.style.background = steamQRStatus === 'success' ? '#f5f5f5' : '#e8e8e8'"
                @mouseleave="$event.currentTarget.style.background = '#f5f5f5'"
              >
                <div v-if="!steamQRCode && !steamQRLoading">
                  <el-icon :size="80" color="#409EFF"><Grid /></el-icon>
                  <p style="color: #409EFF; margin-top: 10px; font-weight: 500;">点击获取Steam登录二维码</p>
                </div>
                <div v-else-if="steamQRLoading">
                  <el-icon :size="80" class="is-loading" color="#409EFF"><Loading /></el-icon>
                  <p style="color: #409EFF; margin-top: 10px;">正在获取二维码...</p>
                </div>
                <div v-else>
                  <img :src="steamQRCode" alt="Steam登录二维码" style="width: 200px; height: 200px;" />
                  <p style="color: #666; margin-top: 10px; font-size: 14px;">
                    请使用Steam手机APP扫描二维码
                  </p>
                  <el-tag :type="steamQRStatus === 'waiting' ? 'info' : steamQRStatus === 'success' ? 'success' : 'warning'" style="margin-top: 10px;">
                    {{ getSteamQRStatusText() }}
                  </el-tag>
                  <div v-if="steamQRStatus === 'expired'" style="margin-top: 10px;">
                    <el-link type="primary" :underline="false" @click.stop="handleGenerateQRCode">
                      点击刷新二维码
                    </el-link>
                  </div>
                </div>
              </div>
            </el-form-item>
          </template>

          <!-- 账号密码登录 -->
          <template v-else-if="inputForm.steamLoginMethod === 'password'">
            <el-form-item label="Steam用户名" required>
              <el-input 
                v-model="inputForm.steamUsername" 
                placeholder="请输入Steam用户名"
              />
            </el-form-item>
            <el-form-item label="Steam密码" required>
              <el-input 
                v-model="inputForm.steamPassword" 
                type="password"
                show-password
                placeholder="请输入Steam密码"
              />
            </el-form-item>
            <el-form-item label="Steam PIN">
              <el-input 
                v-model="inputForm.steamTwofactorCode" 
                placeholder="请输入5位Steam Guard验证码（如需要）"
                maxlength="5"
              />
              <div style="color: #999; font-size: 12px; margin-top: 5px;">
                如果您的账号启用了Steam Guard手机令牌，请在此输入验证码
              </div>
            </el-form-item>
            <el-form-item>
              <el-button 
                type="success" 
                @click="handleSteamLogin" 
                :loading="steamLoginLoading"
                style="width: 100%;"
              >
                {{ steamLoginLoading ? '登录中...' : '立即登录获取Cookie' }}
              </el-button>
            </el-form-item>
          </template>

          <el-form-item label="SteamID" required>
            <el-input 
              v-model="inputForm.steamID" 
              placeholder="请输入SteamID"
            />
          </el-form-item>
          
          
          <!-- 登录状态提示 -->
          <el-alert
            v-if="inputForm.steamLoginMessage"
            :title="inputForm.steamLoginMessage"
            :type="inputForm.steamLoginSuccess ? 'success' : 'warning'"
            :closable="false"
            show-icon
            style="margin-top: 10px;"
          />

          <el-form-item label="基础Cookies">
            <el-input 
              v-model="inputForm.steamBaseCookies" 
              type="textarea"
              :rows="3"
              placeholder="扫码或登录成功后自动填入，可手动粘贴基础Cookie"
            />
            <div style="color: #999; font-size: 12px; margin-top: 4px;">
              建议同时保存基础Cookies，以便后续校验或刷新登录状态。
            </div>
          </el-form-item>
          <el-form-item label="库存Cookies" required>
            <el-input 
              v-model="inputForm.steamInventoryCookies" 
              type="textarea"
              :rows="3"
              placeholder="访问库存页后的完整Cookie，采集库存使用该值"
            />
            <div style="color: #999; font-size: 12px; margin-top: 4px;">
              库存Cookies需可以访问 <code>inventory/730/16</code> 接口。
            </div>
          </el-form-item>
        </template>

        <!-- 完美世界APP特有配置 -->
        <PerfectWorldForm
          v-else-if="inputForm.type === 'perfectworld'"
          ref="perfectWorldFormRef"
          :form="inputForm"
          :is-edit-mode="false"
          :proxy-address="proxyAddress"
          @update:form="Object.assign(inputForm, $event)"
          @update:proxyAddress="proxyAddress = $event"
          @token-success="handleSubmit"
        />
        
        <!-- 完美世界APP特有配置 (旧代码保留，待删除) -->
        <template v-if="false && inputForm.type === 'perfectworld'">
          <el-form-item>
            <el-button 
              type="success" 
              @click="startPerfectWorldTokenCollection(false)" 
              :loading="perfectWorldTokenLoading"
              :disabled="perfectWorldTokenStatus === 'success'"
              style="width: 100%;"
            >
              <el-icon style="margin-right: 5px;"><Grid /></el-icon>
              {{ perfectWorldTokenLoading ? '正在获取令牌...' : perfectWorldTokenStatus === 'success' ? '✓ 令牌已获取' : '一键获取完美世界APP令牌' }}
            </el-button>
            <div v-if="perfectWorldTokenStatus === 'waiting'" style="margin-top: 10px; padding: 10px; background: #fff7e6; border-radius: 4px; border-left: 3px solid #faad14;">
              <div style="color: #faad14; font-weight: 500; margin-bottom: 5px;">
                <el-icon><Loading /></el-icon> 等待手机APP访问...
              </div>
              <div style="color: #666; font-size: 12px;">
                1. 在手机WiFi设置中配置代理: <strong>{{ proxyAddress || '...' }}</strong><br/>
                2. 打开完美世界APP并登录<br/>
                3. 系统将自动获取令牌
              </div>
            </div>
            <div v-if="perfectWorldTokenStatus === 'success'" style="margin-top: 10px; padding: 10px; background: #f6ffed; border-radius: 4px; border-left: 3px solid #52c41a;">
              <div style="color: #52c41a; font-weight: 500;">
                <el-icon><CircleCheck /></el-icon> 令牌获取成功!
              </div>
            </div>
          </el-form-item>
          
          <!-- 完美世界配置 -->
          <el-collapse v-model="inputPerfectWorldCollapse">
            <el-collapse-item title="完美世界APP配置" name="config">
              <el-form-item label="appversion" required>
                <el-input 
                  v-model="inputForm.appversion" 
                  placeholder="请输入appversion"
                />
              </el-form-item>
              <el-form-item label="device" required>
                <el-input 
                  v-model="inputForm.device" 
                  placeholder="请输入device"
                />
              </el-form-item>
              <el-form-item label="gameType" required>
                <el-input 
                  v-model="inputForm.gameType" 
                  placeholder="请输入gameType"
                />
              </el-form-item>
              <el-form-item label="platform" required>
                <el-input 
                  v-model="inputForm.platform" 
                  placeholder="请输入platform"
                />
              </el-form-item>
              <el-form-item label="token" required>
                <el-input 
                  v-model="inputForm.pwToken" 
                  type="textarea"
                  :rows="2"
                  placeholder="请输入token"
                />
              </el-form-item>
              <el-form-item label="tdSign" required>
                <el-input 
                  v-model="inputForm.tdSign" 
                  type="textarea"
                  :rows="2"
                  placeholder="请输入tdSign"
                />
              </el-form-item>
              <el-form-item label="SteamID" required>
                <el-input 
                  v-model="inputForm.pwSteamID" 
                  placeholder="请输入SteamID"
                />
              </el-form-item>
              <el-form-item label="更新频率">
                <el-select v-model="inputForm.updateFreq" placeholder="选择更新频率" style="width: 100%;">
                  <el-option label="每15分钟" value="15min" />
                  <el-option label="每小时" value="1hour" />
                  <el-option label="每3小时" value="3hour" />
                  <el-option label="每6小时" value="6hour" />
                  <el-option label="每12小时" value="12hour" />
                  <el-option label="每天" value="daily" />
                </el-select>
              </el-form-item>
            </el-collapse-item>
          </el-collapse>
        </template>
        
        <!-- CsFloat特有配置 -->
        <CsfloatForm
          v-else-if="inputForm.type === 'csfloat'"
          ref="csfloatFormRef"
          :form="inputForm"
          :is-edit-mode="false"
          :proxy-address="proxyAddress"
          @update:form="Object.assign(inputForm, $event)"
          @update:proxyAddress="proxyAddress = $event"
          @token-success="handleSubmit"
        />
        
        <!-- CsFloat特有配置 (旧代码保留，待删除) -->
        <template v-if="false && inputForm.type === 'csfloat'">
          <el-form-item>
            <el-button 
              type="success" 
              @click="startCsfloatTokenCollection(false)" 
              :loading="csfloatTokenLoading"
              :disabled="csfloatTokenStatus === 'success'"
              style="width: 100%;"
            >
              <el-icon style="margin-right: 5px;"><Grid /></el-icon>
              {{ csfloatTokenLoading ? '正在获取令牌...' : csfloatTokenStatus === 'success' ? '✓ 令牌已获取' : '一键获取CsFloat令牌' }}
            </el-button>
            <div v-if="csfloatTokenStatus === 'waiting'" style="margin-top: 10px; padding: 10px; background: #fff7e6; border-radius: 4px; border-left: 3px solid #faad14;">
              <div style="color: #faad14; font-weight: 500; margin-bottom: 5px;">
                <el-icon><Loading /></el-icon> 等待浏览器访问...
              </div>
              <div style="color: #666; font-size: 12px;">
                1. 在浏览器中配置代理: <strong>{{ proxyAddress || '...' }}</strong><br/>
                2. 访问 https://csfloat.com 并登录<br/>
                3. 系统将自动获取令牌
              </div>
            </div>
            <div v-if="csfloatTokenStatus === 'success'" style="margin-top: 10px; padding: 10px; background: #f6ffed; border-radius: 4px; border-left: 3px solid #52c41a;">
              <div style="color: #52c41a; font-weight: 500;">
                <el-icon><CircleCheck /></el-icon> 令牌获取成功!
              </div>
            </div>
          </el-form-item>
          
          <el-collapse v-model="inputCsfloatCollapse">
            <el-collapse-item title="CsFloat配置" name="config">
              <el-form-item label="User-Agent" required>
                <el-input 
                  v-model="inputForm.csfloatUserAgent" 
                  placeholder="请输入User-Agent"
                />
              </el-form-item>
              <el-form-item label="Referer" required>
                <el-input 
                  v-model="inputForm.csfloatReferer" 
                  placeholder="请输入Referer"
                />
              </el-form-item>
              <el-form-item label="Accept" required>
                <el-input 
                  v-model="inputForm.csfloatAccept" 
                  placeholder="请输入Accept"
                />
              </el-form-item>
              <el-form-item label="X-App-Version" required>
                <el-input 
                  v-model="inputForm.csfloatXAppVersion" 
                  placeholder="请输入X-App-Version"
                />
              </el-form-item>
              <el-form-item label="Host" required>
                <el-input 
                  v-model="inputForm.csfloatHost" 
                  placeholder="请输入Host"
                />
              </el-form-item>
              <el-form-item label="Connection" required>
                <el-input 
                  v-model="inputForm.csfloatConnection" 
                  placeholder="请输入Connection"
                />
              </el-form-item>
              <el-form-item label="Accept-Encoding" required>
                <el-input 
                  v-model="inputForm.csfloatAcceptEncoding" 
                  placeholder="请输入Accept-Encoding"
                />
              </el-form-item>
              <el-form-item label="Cookie" required>
                <el-input 
                  v-model="inputForm.csfloatCookie" 
                  type="textarea"
                  :rows="3"
                  placeholder="请输入Cookie"
                />
              </el-form-item>
              <el-form-item label="SteamID" required>
                <el-input 
                  v-model="inputForm.csfloatSteamID" 
                  placeholder="请输入SteamID"
                />
              </el-form-item>
            </el-collapse-item>
          </el-collapse>
        </template>

        <!-- CSQAQ特有配置 -->
        <CsqaqForm
          v-else-if="inputForm.type === 'csqaq'"
          :form="inputForm"
          :is-edit-mode="false"
          @update:form="Object.assign(inputForm, $event)"
        />

        <!-- SteamDT特有配置 -->
        <SteamdtForm
          v-else-if="inputForm.type === 'steamdt'"
          :form="inputForm"
          :is-edit-mode="false"
          @update:form="Object.assign(inputForm, $event)"
        />
        
        <!-- 通用配置 -->
        <template v-else-if="inputForm.type && inputForm.type !== 'youpin' && inputForm.type !== 'steam' && inputForm.type !== 'perfectworld' && inputForm.type !== 'csfloat' && inputForm.type !== 'csqaq' && inputForm.type !== 'steamdt'">
          <el-form-item label="API地址">
            <el-input 
              v-model="inputForm.apiUrl" 
              placeholder="请输入API地址"
            />
          </el-form-item>
          <el-form-item label="API密钥">
            <el-input 
              v-model="inputForm.apiKey" 
              type="password"
              show-password
              placeholder="请输入API密钥"
            />
          </el-form-item>
        </template>
        
        <!-- 悠悠有品特有配置 -->
        <YoupinForm
          v-if="inputForm.type === 'youpin'"
          ref="youpinFormRef"
          :form="inputForm"
          :is-edit-mode="false"
          :proxy-address="proxyAddress"
          @update:form="Object.assign(inputForm, $event)"
          @update:proxyAddress="proxyAddress = $event"
          @token-success="handleSubmit"
        />
        
        <!-- 悠悠有品特有配置 (旧代码保留，待删除) -->
        <template v-if="false && inputForm.type === 'youpin'">
          <!-- 登录方式选择 -->
          <el-form-item label="登录方式" required>
            <el-radio-group v-model="inputForm.yyypLoginMethod">
              <el-radio label="sms">短信登录</el-radio>
              <el-radio label="capture">通过抓包获取</el-radio>
            </el-radio-group>
          </el-form-item>

          <!-- 短信登录方式 -->
          <template v-if="inputForm.yyypLoginMethod === 'sms'">
            <el-form-item label="Session ID" required>
              <div style="display: flex; gap: 10px;">
                <el-input 
                  v-model="inputForm.yyypSessionId" 
                  placeholder="点击生成按钮生成Session ID"
                  style="flex: 1;"
                  readonly
                  disabled
                />
                <el-button 
                  type="primary" 
                  @click="handleGenerateSessionId"
                  :loading="generatingSessionId"
                >
                  生成SessionID
                </el-button>
              </div>
            </el-form-item>
            <el-form-item label="Device ID" required>
              <div style="display: flex; gap: 10px;">
                <el-input 
                  v-model="inputForm.yyypDeviceId" 
                  placeholder="点击生成按钮生成Device ID"
                  style="flex: 1;"
                  readonly
                  disabled
                />
                <el-button 
                  type="primary" 
                  @click="handleGenerateDeviceId"
                  :loading="generatingDeviceId"
                >
                  生成DeviceID
                </el-button>
              </div>
            </el-form-item>
            <el-form-item label="手机号" required>
              <el-input 
                v-model="inputForm.yyypPhone" 
                placeholder="请输入手机号"
                maxlength="11"
              />
            </el-form-item>
            <el-form-item label="验证码">
              <div style="display: flex; gap: 10px;">
                <el-input 
                  v-model="inputForm.yyypSmsCode" 
                  placeholder="请输入短信验证码"
                  maxlength="6"
                  style="flex: 1;"
                />
                <el-button 
                  type="primary" 
                  @click="handleSendSmsCode"
                  :disabled="smsCodeCountdown > 0"
                  :loading="sendingSmsCode"
                >
                  {{ smsCodeCountdown > 0 ? `${smsCodeCountdown}秒后重试` : '发送验证码' }}
                </el-button>
              </div>
            </el-form-item>
            <el-form-item>
              <el-button 
                type="success" 
                @click="handleYyypSmsLogin" 
                :loading="yyypSmsLoginLoading"
                style="width: 100%;"
              >
                <el-icon style="margin-right: 5px;"><Grid /></el-icon>
                {{ yyypSmsLoginLoading ? '登录中...' : '短信登录' }}
              </el-button>
              <div v-if="yyypSmsLoginStatus === 'success'" style="margin-top: 10px; padding: 10px; background: #f6ffed; border-radius: 4px; border-left: 3px solid #52c41a;">
                <div style="color: #52c41a; font-weight: 500;">
                  <el-icon><CircleCheck /></el-icon> 登录成功！配置信息已自动填充
                </div>
              </div>
            </el-form-item>
          </template>

          <!-- 通过抓包获取方式 -->
          <template v-else-if="inputForm.yyypLoginMethod === 'capture'">
            <el-form-item>
              <el-button 
                type="success" 
                @click="startYyypTokenCollection(false)" 
                :loading="yyypTokenLoading"
                :disabled="yyypTokenStatus === 'success'"
                style="width: 100%;"
              >
                <el-icon style="margin-right: 5px;"><Grid /></el-icon>
                {{ yyypTokenLoading ? '正在获取令牌...' : yyypTokenStatus === 'success' ? '✓ 令牌已获取' : '一键获取悠悠有品令牌' }}
              </el-button>
              <div v-if="yyypTokenStatus === 'waiting'" style="margin-top: 10px; padding: 10px; background: #fff7e6; border-radius: 4px; border-left: 3px solid #faad14;">
                <div style="color: #faad14; font-weight: 500; margin-bottom: 5px;">
                  <el-icon><Loading /></el-icon> 等待手机APP访问...
                </div>
                <div style="color: #666; font-size: 12px;">
                  1. 在手机WiFi设置中配置代理: <strong>{{ proxyAddress || '...' }}</strong><br/>
                  2. 打开悠悠有品APP并登录<br/>
                  3. 系统将自动获取令牌
                </div>
              </div>
              <div v-if="yyypTokenStatus === 'success'" style="margin-top: 10px; padding: 10px; background: #f6ffed; border-radius: 4px; border-left: 3px solid #52c41a;">
                <div style="color: #52c41a; font-weight: 500;">
                  <el-icon><CircleCheck /></el-icon> 令牌获取成功!
                </div>
              </div>
            </el-form-item>
          </template>

          <!-- 配置信息折叠面板 - 仅在抓包方式或登录成功后显示 -->
          <el-collapse v-if="inputForm.yyypLoginMethod === 'capture' || yyypSmsLoginStatus === 'success'" v-model="inputYyypConfigCollapse" style="margin-top: 20px;">
            <el-collapse-item title="配置信息（可选）" name="config">
              <el-alert 
                title="提示" 
                type="info" 
                :closable="false"
                style="margin-bottom: 15px;"
              >
                短信登录成功后，配置信息已自动填充。如需修改，可在此处编辑。
              </el-alert>
          <el-form-item label="手机号" required>
            <el-input 
              v-model="inputForm.phone" 
              placeholder="请输入手机号"
            />
          </el-form-item>
          <el-form-item label="Session ID" required>
            <el-input 
              v-model="inputForm.sessionid" 
              placeholder="请输入Session ID"
            />
          </el-form-item>
          <el-form-item label="Token" required>
            <el-input 
              v-model="inputForm.token" 
              type="textarea"
              :rows="2"
              placeholder="请输入Token"
            />
          </el-form-item>
          <el-form-item label="设备名称" required>
            <el-input 
              v-model="inputForm.deviceName" 
              placeholder="请输入设备名称"
            />
          </el-form-item>
          <el-form-item label="应用版本" required>
            <el-input 
              v-model="inputForm.appVersion" 
              placeholder="请输入应用版本"
            />
          </el-form-item>
          <el-form-item label="应用类型" required>
            <el-input 
              v-model="inputForm.appType" 
              placeholder="请输入应用类型"
            />
          </el-form-item>
          <el-form-item label="用户ID" required>
            <el-input 
              v-model="inputForm.userId" 
              placeholder="请输入用户ID"
            />
          </el-form-item>
          <el-form-item label="SteamID" required>
            <el-input 
              v-model="inputForm.steamId" 
              placeholder="请输入SteamID"
            />
          </el-form-item>
          <el-form-item label="Device Token" required>
            <el-input 
              v-model="inputForm.devicetoken" 
              placeholder="请输入Device Token"
            />
          </el-form-item>
          <el-form-item label="Device ID" required>
            <el-input 
              v-model="inputForm.deviceid" 
              placeholder="请输入Device ID"
            />
          </el-form-item>
          <el-form-item label="Device UK" required>
            <el-input 
              v-model="inputForm.deviceuk" 
              type="textarea"
              :rows="2"
              placeholder="请输入Device UK"
            />
          </el-form-item>
          <el-form-item label="UK" required>
            <el-input 
              v-model="inputForm.uk" 
              type="textarea"
              :rows="2"
              placeholder="请输入UK"
            />
          </el-form-item>
          <el-form-item label="SK" required>
            <el-input 
              v-model="inputForm.sk" 
              type="textarea"
              :rows="3"
              placeholder="请输入SK"
            />
          </el-form-item>
          <el-form-item label="Tracestate" required>
            <el-input 
              v-model="inputForm.tracestate" 
              type="textarea"
              :rows="2"
              placeholder="请输入Tracestate"
            />
          </el-form-item>
          <el-form-item label="Device Info" required>
            <el-input 
              v-model="inputForm.deviceInfo" 
              type="textarea"
              :rows="2"
              placeholder="请输入Device Info (JSON格式)"
            />
          </el-form-item>
            </el-collapse-item>
          </el-collapse>
        </template>
        
        <el-form-item v-if="['youpin', 'buff', 'steam', 'csfloat'].includes(inputForm.type)" label="是否自动采集">
          <el-switch v-model="inputForm.enabled" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="addDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            添加数据源
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>


<script>
import { Plus, User, Grid, Loading, CircleCheck, DataAnalysis } from '@element-plus/icons-vue'
import { useDataSource } from './useDataSource.js'
import SteamForm from './TransactionSource/SteamForm/index.vue'
import YoupinForm from './TransactionSource/YoupinForm/index.vue'
import BuffForm from './TransactionSource/BuffForm/index.vue'
import PerfectWorldForm from './TransactionSource/PerfectWorldForm/index.vue'
import CsfloatForm from './TransactionSource/CsfloatForm/index.vue'
import CsqaqForm from './QuerySorurce/CsqaqForm/index.vue'
import SteamdtForm from './QuerySorurce/SteamdtForm/index.vue'

export default {
  name: 'DataSource',
  components: {
    Plus,
    User,
    Grid,
    Loading,
    CircleCheck,
    DataAnalysis,
    SteamForm,
    YoupinForm,
    BuffForm,
    PerfectWorldForm,
    CsfloatForm,
    CsqaqForm,
    SteamdtForm
  },
  setup() {
    return useDataSource()
  }
}
</script>

<style scoped src="./styles.css"></style>
