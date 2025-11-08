<template>
  <div class="database-manager-wrapper">
    <div class="database-manager-container">
      <div class="page-header">
        <h2>数据库管理器</h2>
        <p class="description">类似Navicat的数据库管理工具，支持查看表结构、编辑数据、执行SQL查询</p>
      </div>

      <div class="manager-layout">
      <!-- 左侧：表列表 -->
      <div class="sidebar" :class="{ collapsed: sidebarCollapsed }">
        <div class="sidebar-header">
          <el-icon><Files /></el-icon>
          <span v-if="!sidebarCollapsed">数据表</span>
          <el-button 
            v-if="!sidebarCollapsed"
            type="primary" 
            size="small" 
            @click="refreshTables"
            :loading="tablesLoading"
          >
            <el-icon><Refresh /></el-icon>
          </el-button>
        </div>
        
        <div class="sidebar-content">
          <el-input
            v-if="!sidebarCollapsed"
            v-model="tableSearchQuery"
            placeholder="搜索表名..."
            :prefix-icon="Search"
            size="small"
            clearable
            style="margin-bottom: 10px;"
          />
          
          <div class="table-list">
            <div 
              v-for="table in filteredTables" 
              :key="table.name"
              class="table-item"
              :class="{ active: selectedTable === table.name }"
              @click="selectTable(table.name)"
              :title="table.name"
            >
              <el-icon><Document /></el-icon>
              <span v-if="!sidebarCollapsed" class="table-name">{{ table.name }}</span>
              <el-tag v-if="!sidebarCollapsed" size="small" type="info">{{ table.rowCount }}</el-tag>
            </div>
          </div>
        </div>
        
        <div class="sidebar-footer">
          <el-button 
            text 
            @click="sidebarCollapsed = !sidebarCollapsed"
            style="width: 100%;"
          >
            <el-icon>
              <DArrowLeft v-if="!sidebarCollapsed" />
              <DArrowRight v-else />
            </el-icon>
          </el-button>
        </div>
      </div>

      <!-- 右侧：主内容区 -->
      <div class="main-content">
        <!-- 空状态 -->
        <div v-if="!selectedTable" class="empty-state">
          <el-empty description="请从左侧选择一个数据表" />
        </div>

        <!-- 表详情 -->
        <div v-else class="table-detail">
          <!-- 工具栏 -->
          <div class="toolbar">
            <div class="toolbar-left">
              <h3>{{ selectedTable }}</h3>
              <el-tag type="info">{{ tableData.length }} 行</el-tag>
            </div>
            <div class="toolbar-right">
              <el-button-group>
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
              </el-button-group>
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
                <el-input
                  v-model="dataSearchQuery"
                  placeholder="搜索数据..."
                  :prefix-icon="Search"
                  size="small"
                  clearable
                  style="width: 200px;"
                />
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
              max-height="600"
              border
              stripe
              @selection-change="handleSelectionChange"
              v-loading="tableLoading"
            >
              <el-table-column type="selection" width="55" fixed />
              <el-table-column 
                v-for="column in tableColumns" 
                :key="column.name"
                :prop="column.name"
                :label="column.name"
                :width="column.width || 150"
                show-overflow-tooltip
              >
                <template #default="{ row }">
                  <span>{{ formatCellValue(row[column.name]) }}</span>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="150" fixed="right">
                <template #default="{ row, $index }">
                  <el-button type="primary" size="small" @click="editRow(row, $index)">
                    编辑
                  </el-button>
                  <el-button type="danger" size="small" @click="deleteRow(row, $index)">
                    删除
                  </el-button>
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Search } from '@element-plus/icons-vue';
import axios from 'axios';

// 侧边栏
const sidebarCollapsed = ref(false);
const tableSearchQuery = ref('');
const tables = ref([]);
const tablesLoading = ref(false);

// 选中的表
const selectedTable = ref('');
const activeTab = ref('data');

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

// 计算属性
const filteredTables = computed(() => {
  if (!tableSearchQuery.value) return tables.value;
  return tables.value.filter(table => 
    table.name.toLowerCase().includes(tableSearchQuery.value.toLowerCase())
  );
});

const filteredTableData = computed(() => {
  if (!dataSearchQuery.value) return tableData.value;
  return tableData.value.filter(row => {
    return Object.values(row).some(value => 
      String(value).toLowerCase().includes(dataSearchQuery.value.toLowerCase())
    );
  });
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

// 选择表
const selectTable = async (tableName) => {
  selectedTable.value = tableName;
  activeTab.value = 'data';
  await loadTableData();
  await loadTableStructure();
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

// 初始化
onMounted(() => {
  refreshTables();
  loadSavedQueries();
});
</script>

<style scoped>
.database-manager-wrapper {
  width: 100%;
  height: 100%;
  background: #f5f7fa;
  overflow: hidden;
}

.database-manager-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.page-header {
  padding: 20px;
  background: white;
  border-bottom: 1px solid #ebeef5;
  flex-shrink: 0;
}

.page-header h2 {
  font-size: 24px;
  color: #303133;
  margin: 0 0 8px 0;
}

.description {
  color: #606266;
  font-size: 14px;
  margin: 0;
}

.manager-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
  min-height: 0;
}

/* 侧边栏 */
.sidebar {
  width: 280px;
  background: white;
  border-right: 1px solid #ebeef5;
  display: flex;
  flex-direction: column;
  transition: width 0.3s;
}

.sidebar.collapsed {
  width: 60px;
}

.sidebar-header {
  padding: 15px;
  border-bottom: 1px solid #ebeef5;
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.table-list {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.table-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.table-item:hover {
  background: #f5f7fa;
}

.table-item.active {
  background: #ecf5ff;
  color: #409eff;
}

.table-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sidebar-footer {
  padding: 10px;
  border-top: 1px solid #ebeef5;
}

/* 主内容区 */
.main-content {
  flex: 1;
  overflow: auto;
  background: white;
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
  border-bottom: 1px solid #ebeef5;
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
  color: #303133;
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
  border-bottom: 1px solid #ebeef5;
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
}

.structure-info,
.structure-sql {
  margin-top: 30px;
}

.structure-info h4,
.structure-sql h4 {
  font-size: 16px;
  color: #303133;
  margin: 0 0 15px 0;
}

/* 查询视图 */
.query-view {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 20px;
  gap: 20px;
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
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 15px;
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
  color: #303133;
}
</style>
