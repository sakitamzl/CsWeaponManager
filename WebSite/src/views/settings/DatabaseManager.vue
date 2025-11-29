<template>
  <div class="database-manager-wrapper">
    <div class="database-manager-container">
      <!-- Navicat 风格布局：左侧表列表 + 右侧内容 -->
      <div class="navicat-layout">
        <!-- 左侧表列表 -->
        <div class="left-sidebar">
          <!-- 数据库信息项 -->
          <div 
            :class="['sidebar-header', 'database-info-header', { active: !selectedTable }]"
            @click="showDatabaseInfo"
          >
            <h3>📊 数据库信息</h3>
          </div>
          
          <div class="tables-list">
            <!-- 表列表 -->
            <div 
              v-for="table in tables" 
              :key="table.name"
              :class="['table-item', { active: selectedTable === table.name }]"
              @click="selectTable(table.name)"
            >
              <div class="table-name">{{ table.name }}</div>
              <div class="table-count">{{ table.rowCount }}</div>
            </div>
          </div>
        </div>

        <!-- 右侧内容区 -->
        <div class="right-content">
          <!-- 数据库首页 - 未选择表时显示 -->
          <div v-if="!selectedTable" class="database-home">
            <!-- 数据库信息 -->
            <div class="info-view">
            <el-card class="info-card">
              <template #header>
                <div class="card-header">
                  <span>数据库信息</span>
                  <el-button type="primary" size="small" @click="refreshDatabaseInfo" :loading="databaseInfoLoading">
                    <el-icon><Refresh /></el-icon>
                    刷新
                  </el-button>
                </div>
              </template>
              <el-descriptions :column="2" border>
                <el-descriptions-item label="数据库文件">{{ databaseInfo.name || 'csweaponmanager.db' }}</el-descriptions-item>
                <el-descriptions-item label="文件大小">{{ formatSize(databaseInfo.size) }}</el-descriptions-item>
                <el-descriptions-item label="表数量">{{ tables.length }}</el-descriptions-item>
                <el-descriptions-item label="总行数">{{ databaseInfo.totalRows || 0 }}</el-descriptions-item>
                <el-descriptions-item label="创建时间" :span="2">{{ databaseInfo.createTime || 'N/A' }}</el-descriptions-item>
                <el-descriptions-item label="最后修改时间" :span="2">{{ databaseInfo.modifyTime || 'N/A' }}</el-descriptions-item>
                <el-descriptions-item label="文件路径" :span="2">{{ databaseInfo.path || 'N/A' }}</el-descriptions-item>
              </el-descriptions>
            </el-card>

            <el-card class="info-card" style="margin-top: 20px;">
              <template #header>
                <div class="card-header">
                  <span>数据库操作</span>
                </div>
              </template>
              <div class="database-actions">
                <el-button type="success" @click="backupDatabase" :loading="backupLoading">
                  <el-icon><FolderAdd /></el-icon>
                  备份数据库
                </el-button>
                <el-button type="primary" @click="downloadDatabase" :loading="downloadLoading">
                  <el-icon><Download /></el-icon>
                  下载数据库
                </el-button>
                <el-button type="warning" @click="showRestoreDialog">
                  <el-icon><Upload /></el-icon>
                  恢复数据库
                </el-button>
                <el-button type="info" @click="optimizeDatabase" :loading="optimizeLoading">
                  <el-icon><Tools /></el-icon>
                  优化数据库
                </el-button>
                <el-button type="danger" @click="vacuumDatabase" :loading="vacuumLoading">
                  <el-icon><MagicStick /></el-icon>
                  清理数据库
                </el-button>
              </div>
            </el-card>

            <el-card class="info-card" style="margin-top: 20px;">
              <template #header>
                <div class="card-header">
                  <span>表统计</span>
                </div>
              </template>
              <el-table :data="tables" style="width: 100%" border max-height="400">
                <el-table-column prop="name" label="表名" />
                <el-table-column prop="rowCount" label="行数" width="120" sortable />
                <el-table-column label="操作" width="260">
                  <template #default="{ row }">
                    <el-button type="primary" size="small" link @click="selectTable(row.name)">
                      查看
                    </el-button>
                    <el-button type="warning" size="small" link @click="truncateTable(row.name)">
                      清空表
                    </el-button>
                    <el-button type="danger" size="small" link @click="dropTable(row.name)">
                      删除表
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-card>

            <el-card class="info-card" style="margin-top: 20px;">
              <template #header>
                <div class="card-header">
                  <span>SQL 语句执行</span>
                </div>
              </template>
              <div class="sql-executor">
                <div class="sql-toolbar">
                  <el-button type="primary" @click="executeSQL" :loading="sqlExecuting">
                    <el-icon><CaretRight /></el-icon>
                    执行 (F5)
                  </el-button>
                  <el-button @click="clearSQL">
                    <el-icon><Delete /></el-icon>
                    清空
                  </el-button>
                  <el-button @click="formatSQL">
                    <el-icon><MagicStick /></el-icon>
                    格式化
                  </el-button>
                </div>
                <el-input
                  v-model="sqlStatement"
                  type="textarea"
                  :rows="8"
                  placeholder="输入 SQL 语句...&#10;&#10;示例:&#10;SELECT * FROM table_name WHERE condition;&#10;UPDATE table_name SET column = value WHERE condition;&#10;DELETE FROM table_name WHERE condition;"
                  @keydown.f5.prevent="executeSQL"
                  class="sql-input"
                />
                <div class="sql-result" v-if="sqlResult.length > 0 || sqlError">
                  <div class="result-header">
                    <h4>执行结果</h4>
                    <el-tag v-if="sqlResult.length > 0" type="success">
                      {{ sqlResult.length }} 行
                    </el-tag>
                    <el-tag v-if="sqlExecutionTime" type="info">
                      执行时间: {{ sqlExecutionTime }}ms
                    </el-tag>
                  </div>
                  <el-alert
                    v-if="sqlError"
                    :title="sqlError"
                    type="error"
                    :closable="false"
                    style="margin-bottom: 10px;"
                  />
                  <el-table
                    v-if="sqlResult.length > 0"
                    :data="sqlResult"
                    style="width: 100%"
                    max-height="300"
                    border
                    stripe
                  >
                    <el-table-column
                      v-for="column in sqlResultColumns"
                      :key="column"
                      :prop="column"
                      :label="column"
                      show-overflow-tooltip
                    />
                  </el-table>
                  <div v-if="sqlMessage" class="sql-message">
                    <el-alert
                      :title="sqlMessage"
                      type="success"
                      :closable="false"
                    />
                  </div>
                  <div v-if="sqlExecutionDetails.length > 0" class="execution-details">
                    <h5>执行详情：</h5>
                    <el-table :data="sqlExecutionDetails" style="width: 100%" border size="small" max-height="200">
                      <el-table-column prop="statement" label="语句" show-overflow-tooltip />
                      <el-table-column prop="type" label="类型" width="100" />
                      <el-table-column label="结果" width="120">
                        <template #default="{ row }">
                          <el-tag v-if="row.type === 'SELECT'" type="success" size="small">
                            {{ row.rows }} 行
                          </el-tag>
                          <el-tag v-else type="info" size="small">
                            {{ row.affected_rows }} 行
                          </el-tag>
                        </template>
                      </el-table-column>
                    </el-table>
                  </div>
                </div>
              </div>
            </el-card>
            </div>
          </div>

          <!-- 表详情 - 选择表后显示 -->
          <div v-else class="table-detail">
            <!-- 工具栏 -->
            <div class="toolbar">
              <div class="toolbar-left">
                <h3>{{ selectedTable }}</h3>
                <el-tag type="info">{{ tableData.length }} 行</el-tag>
              </div>
              <div class="toolbar-right">
                <el-button 
                  :type="activeTab === 'data' ? 'primary' : ''"
                  @click="activeTab = 'data'"
                >
                  <el-icon><Grid /></el-icon>
                  数据
                </el-button>
                <el-button 
                  :type="activeTab === 'structure' ? 'primary' : ''"
                  @click="activeTab = 'structure'"
                >
                  <el-icon><List /></el-icon>
                  结构
                </el-button>
                <el-button 
                  :type="activeTab === 'query' ? 'primary' : ''"
                  @click="activeTab = 'query'"
                >
                  <el-icon><EditPen /></el-icon>
                  查询
                </el-button>
              </div>
            </div>

          <!-- 数据视图 -->
          <div v-show="activeTab === 'data'" class="data-view">
            <div class="data-toolbar">
              <el-button type="primary" size="small" @click="openAddDialog">
                <el-icon><Plus /></el-icon>
                新增
              </el-button>
              <el-button type="danger" size="small" @click="deleteSelected" :disabled="selectedRows.length === 0">
                <el-icon><Delete /></el-icon>
                删除选中 ({{ selectedRows.length }})
              </el-button>
              <el-button size="small" @click="exportCurrentTable">
                <el-icon><Download /></el-icon>
                导出
              </el-button>
              <el-button size="small" @click="refreshTableData">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
              
              <div class="data-toolbar-right">
                <el-button size="small" @click="showFilterDialog">
                  <el-icon><Filter /></el-icon>
                  筛选
                  <el-badge v-if="activeFilters.length > 0" :value="activeFilters.length" class="filter-badge" />
                </el-button>
                <span class="row-count-info">共 {{ filteredTableData.length }} 行</span>
                <el-pagination
                  v-model:current-page="currentPage"
                  v-model:page-size="pageSize"
                  :page-sizes="[10, 20, 50, 100]"
                  :total="filteredTableData.length"
                  layout="sizes, prev, pager, next"
                  small
                  @size-change="handleSizeChange"
                  @current-change="handleCurrentChange"
                />
              </div>
            </div>

            <el-table
              :data="paginatedData"
              style="width: 100%"
              border
              stripe
              @selection-change="handleSelectionChange"
              @sort-change="handleSortChange"
              v-loading="tableLoading"
            >
              <el-table-column type="selection" width="55" fixed="left" />
              <el-table-column label="操作" width="150" fixed="left">
                <template #default="{ row, $index }">
                  <el-button type="primary" size="small" @click="editRow(row, $index)">
                    编辑
                  </el-button>
                  <el-button type="danger" size="small" @click="deleteRow(row, $index)">
                    删除
                  </el-button>
                </template>
              </el-table-column>
              <el-table-column 
                v-for="column in tableColumns" 
                :key="column.name"
                :prop="column.name"
                :label="column.name"
                :width="column.width || 150"
                sortable="custom"
                show-overflow-tooltip
              >
                <template #default="{ row }">
                  <span>{{ formatCellValue(row[column.name]) }}</span>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- 结构视图 -->
          <div v-show="activeTab === 'structure'" class="structure-view">
            <el-table :data="tableStructure" style="width: 100%" border>
              <el-table-column prop="cid" label="ID" width="80" />
              <el-table-column prop="name" label="字段名" width="200" />
              <el-table-column prop="type" label="类型" width="150" />
              <el-table-column prop="notnull" label="非空" width="80">
                <template #default="{ row }">
                  <el-tag :type="row.notnull ? 'success' : 'info'" size="small">
                    {{ row.notnull ? '是' : '否' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="dflt_value" label="默认值" width="150" />
              <el-table-column prop="pk" label="主键" width="80">
                <template #default="{ row }">
                  <el-tag v-if="row.pk" type="danger" size="small">主键</el-tag>
                </template>
              </el-table-column>
            </el-table>

            <div class="structure-info">
              <h4>表信息</h4>
              <el-descriptions :column="2" border>
                <el-descriptions-item label="表名">{{ selectedTable }}</el-descriptions-item>
                <el-descriptions-item label="字段数">{{ tableStructure.length }}</el-descriptions-item>
                <el-descriptions-item label="行数">{{ tableData.length }}</el-descriptions-item>
                <el-descriptions-item label="创建时间">{{ tableInfo.createTime || '-' }}</el-descriptions-item>
              </el-descriptions>
            </div>

            <div class="structure-sql">
              <h4>建表语句</h4>
              <el-input
                v-model="createTableSQL"
                type="textarea"
                :rows="10"
                readonly
              />
              <el-button type="primary" @click="copySQL" style="margin-top: 10px;">
                <el-icon><CopyDocument /></el-icon>
                复制SQL
              </el-button>
            </div>
          </div>

          <!-- 查询视图 -->
          <div v-show="activeTab === 'query'" class="query-view">
            <div class="query-editor">
              <div class="query-toolbar">
                <el-button type="primary" @click="executeQuery" :loading="queryLoading">
                  <el-icon><CaretRight /></el-icon>
                  执行 (F5)
                </el-button>
                <el-button @click="clearQuery">
                  <el-icon><Delete /></el-icon>
                  清空
                </el-button>
                <el-button @click="formatQuery">
                  <el-icon><MagicStick /></el-icon>
                  格式化
                </el-button>
                <el-button @click="saveQuery">
                  <el-icon><DocumentAdd /></el-icon>
                  保存查询
                </el-button>
                
                <el-select 
                  v-model="selectedSavedQuery" 
                  placeholder="选择已保存的查询"
                  style="width: 200px; margin-left: auto;"
                  @change="loadSavedQuery"
                  clearable
                >
                  <el-option
                    v-for="query in savedQueries"
                    :key="query.id"
                    :label="query.name"
                    :value="query.id"
                  />
                </el-select>
              </div>

              <el-input
                v-model="sqlQuery"
                type="textarea"
                :rows="10"
                placeholder="输入SQL查询语句...&#10;&#10;示例:&#10;SELECT * FROM table_name WHERE condition;&#10;UPDATE table_name SET column = value WHERE condition;&#10;DELETE FROM table_name WHERE condition;"
                @keydown.f5.prevent="executeQuery"
              />
            </div>

            <div class="query-result">
              <div class="result-header">
                <h4>查询结果</h4>
                <el-tag v-if="queryResult.length > 0" type="success">
                  {{ queryResult.length }} 行
                </el-tag>
                <el-tag v-if="queryExecutionTime" type="info">
                  执行时间: {{ queryExecutionTime }}ms
                </el-tag>
              </div>

              <el-alert
                v-if="queryError"
                :title="queryError"
                type="error"
                :closable="false"
                style="margin-bottom: 10px;"
              />

              <el-table
                v-if="queryResult.length > 0"
                :data="queryResult"
                style="width: 100%"
                max-height="400"
                border
                stripe
              >
                <el-table-column
                  v-for="column in queryResultColumns"
                  :key="column"
                  :prop="column"
                  :label="column"
                  show-overflow-tooltip
                />
              </el-table>

              <el-empty v-else-if="!queryError" description="执行查询以查看结果" />
            </div>
          </div>
        </div>
        </div>
      </div>
    </div>

    <!-- 编辑/新增对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      :title="editMode === 'add' ? '新增数据' : '编辑数据'"
      width="600px"
    >
      <el-form :model="editForm" label-width="120px">
        <el-form-item
          v-for="column in tableColumns"
          :key="column.name"
          :label="column.name"
        >
          <el-input
            v-model="editForm[column.name]"
            :placeholder="`请输入${column.name}`"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEdit">保存</el-button>
      </template>
    </el-dialog>

    <!-- 保存查询对话框 -->
    <el-dialog v-model="saveQueryDialogVisible" title="保存查询" width="400px">
      <el-form :model="saveQueryForm" label-width="80px">
        <el-form-item label="查询名称">
          <el-input v-model="saveQueryForm.name" placeholder="请输入查询名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="saveQueryDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmSaveQuery">保存</el-button>
      </template>
    </el-dialog>

    <!-- 筛选对话框 -->
    <el-dialog v-model="filterDialogVisible" title="数据筛选" width="600px">
      <div class="filter-container">
        <div v-for="(filter, index) in filters" :key="index" class="filter-row">
          <el-select v-model="filter.field" placeholder="选择字段" style="width: 150px;">
            <el-option
              v-for="column in tableColumns"
              :key="column.name"
              :label="column.name"
              :value="column.name"
            />
          </el-select>
          
          <el-select v-model="filter.operator" placeholder="条件" style="width: 120px;">
            <el-option label="等于" value="=" />
            <el-option label="不等于" value="!=" />
            <el-option label="包含" value="LIKE" />
            <el-option label="不包含" value="NOT LIKE" />
            <el-option label="大于" value=">" />
            <el-option label="小于" value="<" />
            <el-option label="大于等于" value=">=" />
            <el-option label="小于等于" value="<=" />
            <el-option label="为空" value="IS NULL" />
            <el-option label="不为空" value="IS NOT NULL" />
          </el-select>
          
          <el-input 
            v-if="!['IS NULL', 'IS NOT NULL'].includes(filter.operator)"
            v-model="filter.value" 
            placeholder="筛选值" 
            style="flex: 1;"
          />
          
          <el-button 
            type="danger" 
            :icon="Delete" 
            circle 
            size="small"
            @click="removeFilter(index)"
          />
        </div>
        
        <el-button type="primary" @click="addFilter" style="width: 100%; margin-top: 10px;">
          <el-icon><Plus /></el-icon>
          添加筛选条件
        </el-button>
      </div>
      
      <template #footer>
        <el-button @click="clearFilters">清空</el-button>
        <el-button @click="filterDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="applyFilters">应用筛选</el-button>
      </template>
    </el-dialog>

    <!-- 恢复数据库对话框 -->
    <el-dialog v-model="restoreDialogVisible" title="恢复数据库" width="500px">
      <el-alert
        title="警告"
        type="warning"
        description="恢复数据库将覆盖当前数据库，此操作不可逆！请确保已备份当前数据。"
        :closable="false"
        style="margin-bottom: 20px;"
      />
      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :limit="1"
        accept=".db,.sqlite,.sqlite3"
        :on-change="handleFileChange"
      >
        <el-button type="primary">
          <el-icon><Upload /></el-icon>
          选择备份文件
        </el-button>
        <template #tip>
          <div class="el-upload__tip">
            只能上传 .db / .sqlite / .sqlite3 文件
          </div>
        </template>
      </el-upload>
      <div v-if="restoreFile" style="margin-top: 15px;">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="文件名">{{ restoreFile.name }}</el-descriptions-item>
          <el-descriptions-item label="文件大小">{{ formatSize(restoreFile.size) }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="restoreDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="confirmRestore" :disabled="!restoreFile" :loading="restoreLoading">
          确认恢复
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { 
  Search,
  Refresh,
  FolderAdd,
  Download,
  Upload,
  Tools,
  MagicStick,
  Grid,
  List,
  EditPen,
  Plus,
  Delete,
  Filter,
  CopyDocument,
  CaretRight,
  DocumentAdd
} from '@element-plus/icons-vue';
import axios from 'axios';

// 侧边栏
const sidebarCollapsed = ref(false);
const tableSearchQuery = ref('');
const tables = ref([]);
const tablesLoading = ref(false);

// 选中的表
const selectedTable = ref('');
const activeTab = ref('info'); // 默认显示信息页

// 数据库信息
const databaseInfo = ref({});
const databaseInfoLoading = ref(false);
const backupLoading = ref(false);
const downloadLoading = ref(false);
const restoreLoading = ref(false);
const optimizeLoading = ref(false);
const vacuumLoading = ref(false);
const restoreDialogVisible = ref(false);
const restoreFile = ref(null);

// 表数据
const tableData = ref([]);
const tableColumns = ref([]);
const tableStructure = ref([]);
const tableInfo = ref({});
const createTableSQL = ref('');
const tableLoading = ref(false);

// 数据视图
const dataSearchQuery = ref('');
const selectedRows = ref([]);
const currentPage = ref(1);
const pageSize = ref(20);

// 筛选功能
const filterDialogVisible = ref(false);
const filters = ref([]);
const activeFilters = ref([]);

// 排序功能
const sortColumn = ref('');
const sortOrder = ref(''); // 'ascending' or 'descending'

// 编辑对话框
const editDialogVisible = ref(false);
const editMode = ref('add'); // 'add' or 'edit'
const editForm = ref({});
const editIndex = ref(-1);

// 查询视图
const sqlQuery = ref('');
const queryResult = ref([]);
const queryResultColumns = ref([]);
const queryError = ref('');
const queryExecutionTime = ref(0);
const queryLoading = ref(false);

// 保存的查询
const savedQueries = ref([]);
const selectedSavedQuery = ref('');
const saveQueryDialogVisible = ref(false);
const saveQueryForm = ref({ name: '' });

// SQL 执行（数据库首页）
const sqlStatement = ref('');
const sqlResult = ref([]);
const sqlResultColumns = ref([]);
const sqlError = ref('');
const sqlExecutionTime = ref(0);
const sqlExecuting = ref(false);
const sqlMessage = ref('');
const sqlExecutionDetails = ref([]);
const sqlTotalStatements = ref(0);

// 计算属性
const filteredTables = computed(() => {
  if (!tableSearchQuery.value) return tables.value;
  return tables.value.filter(table => 
    table.name.toLowerCase().includes(tableSearchQuery.value.toLowerCase())
  );
});

const filteredTableData = computed(() => {
  let data = [...tableData.value];
  
  // 应用筛选条件
  if (activeFilters.value.length > 0) {
    data = data.filter(row => {
      return activeFilters.value.every(filter => {
        const cellValue = String(row[filter.field] || '');
        const filterValue = String(filter.value || '');
        
        switch (filter.operator) {
          case '=':
            return cellValue === filterValue;
          case '!=':
            return cellValue !== filterValue;
          case 'LIKE':
            return cellValue.toLowerCase().includes(filterValue.toLowerCase());
          case 'NOT LIKE':
            return !cellValue.toLowerCase().includes(filterValue.toLowerCase());
          case '>':
            return parseFloat(cellValue) > parseFloat(filterValue);
          case '<':
            return parseFloat(cellValue) < parseFloat(filterValue);
          case '>=':
            return parseFloat(cellValue) >= parseFloat(filterValue);
          case '<=':
            return parseFloat(cellValue) <= parseFloat(filterValue);
          case 'IS NULL':
            return !cellValue || cellValue === 'NULL' || cellValue === 'null';
          case 'IS NOT NULL':
            return cellValue && cellValue !== 'NULL' && cellValue !== 'null';
          default:
            return true;
        }
      });
    });
  }
  
  // 应用排序
  if (sortColumn.value && sortOrder.value) {
    data.sort((a, b) => {
      const aValue = a[sortColumn.value];
      const bValue = b[sortColumn.value];
      
      // 处理 null/undefined
      if (aValue === null || aValue === undefined) return sortOrder.value === 'ascending' ? 1 : -1;
      if (bValue === null || bValue === undefined) return sortOrder.value === 'ascending' ? -1 : 1;
      
      // 尝试数字比较
      const aNum = parseFloat(aValue);
      const bNum = parseFloat(bValue);
      if (!isNaN(aNum) && !isNaN(bNum)) {
        return sortOrder.value === 'ascending' ? aNum - bNum : bNum - aNum;
      }
      
      // 字符串比较
      const aStr = String(aValue).toLowerCase();
      const bStr = String(bValue).toLowerCase();
      if (sortOrder.value === 'ascending') {
        return aStr.localeCompare(bStr);
      } else {
        return bStr.localeCompare(aStr);
      }
    });
  }
  
  return data;
});

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return filteredTableData.value.slice(start, end);
});

// 加载表列表
const refreshTables = async () => {
  tablesLoading.value = true;
  try {
    const response = await axios.get('/api/database/tables');
    tables.value = response.data;
  } catch (error) {
    ElMessage.error('加载表列表失败：' + (error.response?.data?.message || error.message));
  } finally {
    tablesLoading.value = false;
  }
};

// 显示数据库信息
const showDatabaseInfo = () => {
  selectedTable.value = '';
  refreshDatabaseInfo();
};

// 选择表
const selectTable = async (tableName) => {
  selectedTable.value = tableName;
  activeTab.value = 'data';
  await loadTableData();
  await loadTableStructure();
};

// 表选择变化
const onTableChange = async () => {
  if (selectedTable.value) {
    activeTab.value = 'data';
    await loadTableData();
    await loadTableStructure();
  }
};

// 加载表数据
const loadTableData = async () => {
  if (!selectedTable.value) return;
  
  tableLoading.value = true;
  try {
    const response = await axios.get(`/api/database/table/${selectedTable.value}/data`);
    tableData.value = response.data.rows;
    tableColumns.value = response.data.columns;
  } catch (error) {
    ElMessage.error('加载表数据失败：' + (error.response?.data?.message || error.message));
  } finally {
    tableLoading.value = false;
  }
};

// 加载表结构
const loadTableStructure = async () => {
  if (!selectedTable.value) return;
  
  try {
    const response = await axios.get(`/api/database/table/${selectedTable.value}/structure`);
    tableStructure.value = response.data.structure;
    tableInfo.value = response.data.info;
    createTableSQL.value = response.data.sql;
  } catch (error) {
    ElMessage.error('加载表结构失败：' + (error.response?.data?.message || error.message));
  }
};

// 刷新表数据
const refreshTableData = () => {
  loadTableData();
};

// 格式化单元格值
const formatCellValue = (value) => {
  if (value === null) return 'NULL';
  if (value === undefined) return '';
  if (typeof value === 'object') return JSON.stringify(value);
  return String(value);
};

// 选择变化
const handleSelectionChange = (selection) => {
  selectedRows.value = selection;
};

// 分页
const handleSizeChange = (val) => {
  pageSize.value = val;
  currentPage.value = 1;
};

const handleCurrentChange = (val) => {
  currentPage.value = val;
};

// 打开新增对话框
const openAddDialog = () => {
  editMode.value = 'add';
  editForm.value = {};
  editDialogVisible.value = true;
};

// 编辑行
const editRow = (row, index) => {
  editMode.value = 'edit';
  editForm.value = { ...row };
  editIndex.value = index;
  editDialogVisible.value = true;
};

// 保存编辑
const saveEdit = async () => {
  try {
    if (editMode.value === 'add') {
      await axios.post(`/api/database/table/${selectedTable.value}/row`, editForm.value);
      ElMessage.success('新增成功');
    } else {
      await axios.put(`/api/database/table/${selectedTable.value}/row`, {
        data: editForm.value,
        index: editIndex.value
      });
      ElMessage.success('更新成功');
    }
    editDialogVisible.value = false;
    await loadTableData();
  } catch (error) {
    ElMessage.error('保存失败：' + (error.response?.data?.message || error.message));
  }
};

// 删除行
const deleteRow = async (row, index) => {
  try {
    await ElMessageBox.confirm('确定要删除这条数据吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    });
    
    await axios.delete(`/api/database/table/${selectedTable.value}/row`, {
      data: { row, index }
    });
    
    ElMessage.success('删除成功');
    await loadTableData();
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败：' + (error.response?.data?.message || error.message));
    }
  }
};

// 删除选中
const deleteSelected = async () => {
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedRows.value.length} 条数据吗？`, '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    });
    
    await axios.post(`/api/database/table/${selectedTable.value}/delete-batch`, {
      rows: selectedRows.value
    });
    
    ElMessage.success('批量删除成功');
    selectedRows.value = [];
    await loadTableData();
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败：' + (error.response?.data?.message || error.message));
    }
  }
};

// 导出当前表
const exportCurrentTable = async () => {
  try {
    const response = await axios.get(`/api/database/table/${selectedTable.value}/export`, {
      responseType: 'blob'
    });
    
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `${selectedTable.value}_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    ElMessage.success('导出成功');
  } catch (error) {
    ElMessage.error('导出失败：' + (error.response?.data?.message || error.message));
  }
};

// 复制SQL
const copySQL = () => {
  navigator.clipboard.writeText(createTableSQL.value);
  ElMessage.success('SQL已复制到剪贴板');
};

// 执行查询
const executeQuery = async () => {
  if (!sqlQuery.value.trim()) {
    ElMessage.warning('请输入SQL查询语句');
    return;
  }
  
  queryLoading.value = true;
  queryError.value = '';
  const startTime = Date.now();
  
  try {
    const response = await axios.post('/api/database/query', {
      sql: sqlQuery.value
    });
    
    queryExecutionTime.value = Date.now() - startTime;
    queryResult.value = response.data.rows || [];
    queryResultColumns.value = response.data.columns || [];
    
    ElMessage.success(`查询成功，返回 ${queryResult.value.length} 行`);
  } catch (error) {
    queryError.value = error.response?.data?.message || error.message;
    queryResult.value = [];
    queryResultColumns.value = [];
  } finally {
    queryLoading.value = false;
  }
};

// 清空查询
const clearQuery = () => {
  sqlQuery.value = '';
  queryResult.value = [];
  queryResultColumns.value = [];
  queryError.value = '';
};

// 格式化查询
const formatQuery = () => {
  // 简单的SQL格式化
  let formatted = sqlQuery.value
    .replace(/\s+/g, ' ')
    .replace(/\s*,\s*/g, ',\n  ')
    .replace(/\s+(FROM|WHERE|ORDER BY|GROUP BY|HAVING|LIMIT)/gi, '\n$1')
    .replace(/\s+(AND|OR)/gi, '\n  $1');
  
  sqlQuery.value = formatted.trim();
};

// 保存查询
const saveQuery = () => {
  if (!sqlQuery.value.trim()) {
    ElMessage.warning('请输入SQL查询语句');
    return;
  }
  saveQueryForm.value.name = '';
  saveQueryDialogVisible.value = true;
};

// 确认保存查询
const confirmSaveQuery = async () => {
  if (!saveQueryForm.value.name) {
    ElMessage.warning('请输入查询名称');
    return;
  }
  
  try {
    await axios.post('/api/database/query/save', {
      name: saveQueryForm.value.name,
      sql: sqlQuery.value
    });
    
    ElMessage.success('查询已保存');
    saveQueryDialogVisible.value = false;
    await loadSavedQueries();
  } catch (error) {
    ElMessage.error('保存失败：' + (error.response?.data?.message || error.message));
  }
};

// 筛选功能
const showFilterDialog = () => {
  if (filters.value.length === 0) {
    addFilter();
  }
  filterDialogVisible.value = true;
};

const addFilter = () => {
  filters.value.push({
    field: '',
    operator: '=',
    value: ''
  });
};

const removeFilter = (index) => {
  filters.value.splice(index, 1);
};

const applyFilters = () => {
  activeFilters.value = filters.value.filter(f => f.field && f.operator);
  filterDialogVisible.value = false;
  currentPage.value = 1; // 重置到第一页
  ElMessage.success(`已应用 ${activeFilters.value.length} 个筛选条件`);
};

const clearFilters = () => {
  filters.value = [];
  activeFilters.value = [];
  currentPage.value = 1;
  ElMessage.success('已清空筛选条件');
};

// 排序处理
const handleSortChange = ({ column, prop, order }) => {
  sortColumn.value = prop || '';
  sortOrder.value = order || '';
  currentPage.value = 1; // 重置到第一页
};

// 加载已保存的查询
const loadSavedQueries = async () => {
  try {
    const response = await axios.get('/api/database/query/saved');
    savedQueries.value = response.data;
  } catch (error) {
    console.error('加载已保存查询失败:', error);
  }
};

// 加载已保存的查询
const loadSavedQuery = () => {
  const query = savedQueries.value.find(q => q.id === selectedSavedQuery.value);
  if (query) {
    sqlQuery.value = query.sql;
  }
};

// 数据库信息和操作
const refreshDatabaseInfo = async () => {
  databaseInfoLoading.value = true;
  try {
    const response = await axios.get('/api/database/info');
    databaseInfo.value = response.data;
  } catch (error) {
    ElMessage.error('获取数据库信息失败：' + (error.response?.data?.message || error.message));
  } finally {
    databaseInfoLoading.value = false;
  }
};

const backupDatabase = async () => {
  try {
    await ElMessageBox.confirm(
      '将在数据库目录下创建备份文件，是否继续？',
      '确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info',
      }
    );
    
    backupLoading.value = true;
    const response = await axios.post('/api/database/backup');
    ElMessage.success(response.data.message || '数据库备份成功');
    await refreshDatabaseInfo();
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('备份失败：' + (error.response?.data?.message || error.message));
    }
  } finally {
    backupLoading.value = false;
  }
};

const downloadDatabase = async () => {
  downloadLoading.value = true;
  try {
    const response = await axios.get('/api/database/download', {
      responseType: 'blob'
    });
    
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
    link.setAttribute('download', `csweaponmanager_${timestamp}.db`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    
    ElMessage.success('数据库下载成功');
  } catch (error) {
    ElMessage.error('下载失败：' + (error.response?.data?.message || error.message));
  } finally {
    downloadLoading.value = false;
  }
};

const showRestoreDialog = () => {
  restoreFile.value = null;
  restoreDialogVisible.value = true;
};

const handleFileChange = (file) => {
  restoreFile.value = file.raw;
};

const confirmRestore = async () => {
  if (!restoreFile.value) {
    ElMessage.warning('请选择备份文件');
    return;
  }
  
  try {
    await ElMessageBox.confirm(
      '确定要恢复数据库吗？此操作将覆盖当前所有数据，且不可逆！',
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );
    
    restoreLoading.value = true;
    const formData = new FormData();
    formData.append('file', restoreFile.value);
    
    await axios.post('/api/database/restore', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    
    ElMessage.success('数据库恢复成功，页面将刷新');
    restoreDialogVisible.value = false;
    
    // 刷新页面
    setTimeout(() => {
      window.location.reload();
    }, 1500);
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('恢复失败：' + (error.response?.data?.message || error.message));
    }
  } finally {
    restoreLoading.value = false;
  }
};

const optimizeDatabase = async () => {
  try {
    await ElMessageBox.confirm(
      '优化数据库将执行以下操作：\n1. 收集统计信息优化查询计划\n2. 重建所有索引提高效率\n3. 检查数据库完整性\n\n是否继续？',
      '确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info',
      }
    );
    
    optimizeLoading.value = true;
    const response = await axios.post('/api/database/optimize');
    
    // 显示优化操作详情
    if (response.data.operations && response.data.operations.length > 0) {
      const operations = response.data.operations.join('\n');
      await ElMessageBox.alert(operations, '优化完成', {
        confirmButtonText: '确定',
        type: 'success',
      });
    } else {
      ElMessage.success('数据库优化成功');
    }
    
    await refreshDatabaseInfo();
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('优化失败：' + (error.response?.data?.message || error.message));
    }
  } finally {
    optimizeLoading.value = false;
  }
};

const vacuumDatabase = async () => {
  try {
    await ElMessageBox.confirm(
      '清理数据库将回收未使用的空间，减小文件大小。是否继续？',
      '确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info',
      }
    );
    
    vacuumLoading.value = true;
    await axios.post('/api/database/vacuum');
    ElMessage.success('数据库清理成功');
    await refreshDatabaseInfo();
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('清理失败：' + (error.response?.data?.message || error.message));
    }
  } finally {
    vacuumLoading.value = false;
  }
};

const truncateTable = async (tableName) => {
  try {
    await ElMessageBox.confirm(
      `确定要清空表 "${tableName}" 吗？此操作将删除表中所有数据，但保留表结构。`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );
    
    tableLoading.value = true;
    await axios.post('/api/database/truncate', { tableName });
    ElMessage.success(`表 "${tableName}" 已清空`);
    
    // 刷新表列表和数据库信息
    await refreshTables();
    await refreshDatabaseInfo();
    
    // 如果当前选中的就是这个表，刷新数据
    if (selectedTable.value === tableName) {
      await loadTableData();
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('清空表失败：' + (error.response?.data?.message || error.message));
    }
  } finally {
    tableLoading.value = false;
  }
};

const dropTable = async (tableName) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除表 "${tableName}" 吗？此操作将永久删除表及其所有数据，且无法恢复！`,
      '危险操作',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'error',
        confirmButtonClass: 'el-button--danger',
      }
    );
    
    // 二次确认
    await ElMessageBox.confirm(
      `请再次确认：您真的要删除表 "${tableName}" 吗？`,
      '最终确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'error',
      }
    );
    
    tableLoading.value = true;
    await axios.post('/api/database/drop', { tableName });
    ElMessage.success(`表 "${tableName}" 已删除`);
    
    // 如果删除的是当前选中的表，返回数据库首页
    if (selectedTable.value === tableName) {
      selectedTable.value = null;
    }
    
    // 刷新表列表和数据库信息
    await refreshTables();
    await refreshDatabaseInfo();
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除表失败：' + (error.response?.data?.message || error.message));
    }
  } finally {
    tableLoading.value = false;
  }
};

const formatSize = (bytes) => {
  if (!bytes || bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
};

// SQL 执行功能（数据库首页）
const executeSQL = async () => {
  if (!sqlStatement.value.trim()) {
    ElMessage.warning('请输入 SQL 语句');
    return;
  }
  
  sqlExecuting.value = true;
  sqlError.value = '';
  sqlMessage.value = '';
  sqlResult.value = [];
  sqlResultColumns.value = [];
  sqlExecutionDetails.value = [];
  sqlTotalStatements.value = 0;
  const startTime = Date.now();
  
  try {
    const response = await axios.post('/api/database/query', {
      sql: sqlStatement.value
    });
    
    sqlExecutionTime.value = Date.now() - startTime;
    sqlResult.value = response.data.rows || [];
    sqlResultColumns.value = response.data.columns || [];
    sqlMessage.value = response.data.message || '';
    sqlExecutionDetails.value = response.data.execution_details || [];
    sqlTotalStatements.value = response.data.total_statements || 0;
    
    if (sqlResult.value.length > 0) {
      ElMessage.success(`查询成功，返回 ${sqlResult.value.length} 行`);
    } else if (sqlMessage.value) {
      ElMessage.success(sqlMessage.value);
    } else {
      ElMessage.success('执行成功');
    }
  } catch (error) {
    sqlError.value = error.response?.data?.error || error.response?.data?.message || error.message;
    sqlResult.value = [];
    sqlResultColumns.value = [];
    sqlExecutionDetails.value = error.response?.data?.execution_details || [];
    
    // 显示错误信息，包括哪条语句出错
    if (error.response?.data?.statement_index) {
      ElMessage.error(`执行失败：第 ${error.response.data.statement_index} 条语句出错 - ${sqlError.value}`);
    } else {
      ElMessage.error('执行失败：' + sqlError.value);
    }
  } finally {
    sqlExecuting.value = false;
  }
};

const clearSQL = () => {
  sqlStatement.value = '';
  sqlResult.value = [];
  sqlResultColumns.value = [];
  sqlError.value = '';
  sqlMessage.value = '';
  sqlExecutionTime.value = 0;
  sqlExecutionDetails.value = [];
  sqlTotalStatements.value = 0;
};

const formatSQL = () => {
  // 简单的 SQL 格式化
  let formatted = sqlStatement.value
    .replace(/\s+/g, ' ')
    .replace(/\s*,\s*/g, ',\n  ')
    .replace(/\s+(FROM|WHERE|ORDER BY|GROUP BY|HAVING|LIMIT|SET|UPDATE|DELETE|INSERT INTO|VALUES)/gi, '\n$1')
    .replace(/\s+(AND|OR)/gi, '\n  $1');
  
  sqlStatement.value = formatted.trim();
};

// 初始化
onMounted(() => {
  refreshTables();
  loadSavedQueries();
  refreshDatabaseInfo();
});
</script>

<style scoped>
.database-manager-wrapper {
  width: 100%;
  height: 100%;
  background: #1a1a1a;
  overflow: hidden;
}

.database-manager-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Navicat 风格布局 */
.navicat-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
  min-height: 0;
}

/* 左侧表列表 */
.left-sidebar {
  width: 280px;
  background: #2a2a2a;
  border-right: 1px solid #3a3a3a;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-header {
  padding: 15px 20px;
  border-bottom: 1px solid #3a3a3a;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #252525;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 16px;
  color: #e0e0e0;
  font-weight: 600;
}

.database-info-header {
  cursor: pointer;
  transition: all 0.2s;
  border-left: 3px solid transparent;
}

.database-info-header:hover {
  background: #2d2d2d;
}

.database-info-header.active {
  background: #1e5fa8;
  border-left-color: #409eff;
}

.database-info-header.active h3 {
  color: #fff;
}

.tables-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.table-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
  transition: all 0.2s;
  border-left: 3px solid transparent;
}

.table-item:hover {
  background: #333;
}

.table-item.active {
  background: #1e5fa8;
  border-left-color: #409eff;
}

.table-name {
  flex: 1;
  font-size: 14px;
  color: #e0e0e0;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  min-width: 0;
}

.table-item.active .table-name {
  color: #fff;
}

.table-count {
  font-size: 12px;
  color: #909399;
  margin-left: 8px;
  flex-shrink: 0;
  padding: 2px 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}

.table-item.active .table-count {
  color: rgba(255, 255, 255, 0.9);
  background: rgba(255, 255, 255, 0.2);
}

/* 右侧内容区 */
.right-content {
  flex: 1;
  overflow: auto;
  background: #1a1a1a;
  display: flex;
  flex-direction: column;
}

.empty-state {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.table-detail {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.toolbar {
  padding: 15px 20px;
  border-bottom: 1px solid #3a3a3a;
  background: #2a2a2a;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.toolbar-left h3 {
  margin: 0;
  font-size: 18px;
  color: #e0e0e0;
}

.toolbar-right {
  display: flex;
  gap: 10px;
}

/* 数据视图 */
.data-view {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.data-toolbar {
  padding: 15px 20px;
  border-bottom: 1px solid #3a3a3a;
  background: #2a2a2a;
  display: flex;
  align-items: center;
  gap: 10px;
}

.data-toolbar-right {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 10px;
}

/* 结构视图 */
.structure-view {
  flex: 1;
  overflow: auto;
  padding: 20px;
  background: #1a1a1a;
}

.structure-info,
.structure-sql {
  margin-top: 30px;
}

.structure-info h4,
.structure-sql h4 {
  font-size: 16px;
  color: #e0e0e0;
  margin: 0 0 15px 0;
}

/* 数据库首页 */
.database-home {
  flex: 1;
  overflow: auto;
  background: #1a1a1a;
}

.home-header {
  padding: 30px 20px 20px;
  background: linear-gradient(135deg, #2a2a2a 0%, #1a1a1a 100%);
  border-bottom: 1px solid #3a3a3a;
}

.home-header h2 {
  margin: 0 0 8px 0;
  font-size: 28px;
  color: #e0e0e0;
  font-weight: 600;
}

.home-header p {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

/* 信息视图 */
.info-view {
  flex: 1;
  overflow: auto;
  padding: 20px;
  background: #1a1a1a;
}

.info-card {
  background: #2a2a2a;
  border: 1px solid #3a3a3a;
}

.info-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
  color: #e0e0e0;
}

.database-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

/* 筛选功能 */
.filter-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.filter-row {
  display: flex;
  gap: 10px;
  align-items: center;
}

.filter-badge {
  margin-left: 5px;
}

.row-count-info {
  font-size: 14px;
  color: #909399;
  padding: 0 10px;
}

/* 查询视图 */
.query-view {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 20px;
  gap: 20px;
  background: #1a1a1a;
}

.query-editor {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.query-toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
}

.query-result {
  flex: 1;
  overflow: auto;
  border: 1px solid #3a3a3a;
  border-radius: 4px;
  padding: 15px;
  background: #2a2a2a;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.result-header h4 {
  margin: 0;
  font-size: 16px;
  color: #e0e0e0;
}

/* SQL 执行器样式 */
.sql-executor {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.sql-toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
}

.sql-input {
  width: 100%;
}

.sql-input :deep(.el-textarea__inner) {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  background: #1a1a1a;
  color: #e0e0e0;
  border: 1px solid #3a3a3a;
}

.sql-result {
  border: 1px solid #3a3a3a;
  border-radius: 4px;
  padding: 15px;
  background: #2a2a2a;
}

.sql-result .result-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.sql-result .result-header h4 {
  margin: 0;
  font-size: 16px;
  color: #e0e0e0;
}

.sql-message {
  margin-top: 10px;
}

.execution-details {
  margin-top: 15px;
}

.execution-details h5 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #e0e0e0;
  font-weight: 600;
}
</style>
