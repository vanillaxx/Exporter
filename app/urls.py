from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('import/notoria/', views.import_notoria, name='import_notoria'),
    path('import/stooq/', views.import_stooq, name='import_stooq'),
    path('import/gpw/', views.import_gpw, name='import_gpw'),
    path('export', views.export, name='export'),
    path('manage/home', views.manage, name='manage_home'),
    path('import/replace_data', views.replace_data, name='replace_data'),

    path('manage/companies', views.CompanyView.as_view(), name='companies'),
    path('manage/companies/create', views.CompanyCreateView.as_view(), name='create_company'),
    path('manage/companies/update/<int:pk>', views.CompanyUpdateView.as_view(), name='update_company'),
    path('manage/companies/delete/<int:pk>', views.CompanyDeleteView.as_view(), name='delete_company'),
    path('manage/companies/merge/', views.CompanyMergeView.as_view(), name='merge_company'),
    path('manage/assets', views.AssetsView.as_view(), name='assets'),
    path('manage/assets/create', views.AssetsCreateView.as_view(), name='create_assets'),
    path('manage/assets/update/<int:pk>', views.AssetsUpdateView.as_view(), name='update_assets'),
    path('manage/assets/delete/<int:pk>', views.AssetsDeleteView.as_view(), name='delete_assets'),
    path('manage/assetsCategories', views.AssetsCategoryView.as_view(), name='assets_categories'),
    path('manage/assetsCategories/create', views.AssetsCategoryCreateView.as_view(), name='create_assets_category'),
    path('manage/assetsCategories/update/<int:pk>', views.AssetsCategoryUpdateView.as_view(), name='update_assets_category'),
    path('manage/assetsCategories/delete/<int:pk>', views.AssetsCategoryDeleteView.as_view(), name='delete_assets_category'),
    path('manage/duPont', views.DuPontIndicatorView.as_view(), name='dupont'),
    path('manage/duPont/create', views.DuPontIndicatorCreateView.as_view(), name='create_dupont'),
    path('manage/duPont/update/<int:pk>', views.DuPontIndicatorUpdateView.as_view(), name='update_dupont'),
    path('manage/duPont/delete/<int:pk>', views.DuPontIndicatorDeleteView.as_view(), name='delete_dupont'),
    path('manage/ekdClasses', views.EkdClassView.as_view(), name='ekd_classes'),
    path('manage/ekdClasses/create', views.EkdClassCreateView.as_view(), name='create_ekd_class'),
    path('manage/ekdClasses/update/<int:pk>', views.EkdClassUpdateView.as_view(), name='update_ekd_class'),
    path('manage/ekdClasses/delete/<int:pk>', views.EkdClassDeleteView.as_view(), name='delete_ekd_class'),
    path('manage/ekdSections', views.EkdSectionView.as_view(), name='ekd_sections'),
    path('manage/ekdSections/create', views.EkdSectionCreateView.as_view(), name='create_ekd_section'),
    path('manage/ekdSections/update/<int:pk>', views.EkdSectionUpdateView.as_view(), name='update_ekd_section'),
    path('manage/ekdSections/delete/<int:pk>', views.EkdSectionDeleteView.as_view(), name='delete_ekd_section'),
    path('manage/equityLiabilities', views.EquityLiabilitiesView.as_view(), name='equity_liabilities'),
    path('manage/equityLiabilities/create', views.EquityLiabilitiesCreateView.as_view(), name='create_equity_liabilities'),
    path('manage/equityLiabilities/update/<int:pk>', views.EquityLiabilitiesUpdateView.as_view(), name='update_equity_liabilities'),
    path('manage/equityLiabilities/delete/<int:pk>', views.EquityLiabilitiesDeleteView.as_view(), name='delete_equity_liabilities'),
    path('manage/equityLiabilitiesCategories', views.EquityLiabilitiesCategoryView.as_view(), name='equity_liabilities_categories'),
    path('manage/equityLiabilitiesCategories/create', views.EquityLiabilitiesCategoryCreateView.as_view(), name='create_equity_liabilities_category'),
    path('manage/equityLiabilitiesCategories/update/<int:pk>', views.EquityLiabilitiesCategoryUpdateView.as_view(), name='update_equity_liabilities_category'),
    path('manage/equityLiabilitiesCategories/delete/<int:pk>', views.EquityLiabilitiesCategoryDeleteView.as_view(), name='delete_equity_liabilities_category'),
    path('manage/financial', views.FinancialRatiosView.as_view(), name='financial'),
    path('manage/financial/create', views.FinancialRatiosCreateView.as_view(), name='create_financial'),
    path('manage/financial/update/<int:pk>', views.FinancialRatiosUpdateView.as_view(), name='update_financial'),
    path('manage/financial/delete/<int:pk>', views.FinancialRatiosDeleteView.as_view(), name='delete_financial'),
    path('manage/market', views.MarketValueView.as_view(), name='market'),
    path('manage/market/create', views.MarketValueCreateView.as_view(), name='create_market'),
    path('manage/market/update/<int:pk>', views.MarketValueUpdateView.as_view(), name='update_market'),
    path('manage/market/delete/<int:pk>', views.MarketValueDeleteView.as_view(), name='delete_market'),
    path('manage/stock', views.StockQuoteView.as_view(), name='stock'),
    path('manage/stock/create', views.StockQuoteCreateView.as_view(), name='create_stock'),
    path('manage/stock/update/<int:pk>', views.StockQuoteUpdateView.as_view(), name='update_stock'),
    path('manage/stock/delete/<int:pk>', views.StockQuoteDeleteView.as_view(), name='delete_stock'),

]
