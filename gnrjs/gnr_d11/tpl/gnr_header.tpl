<!-- ================  Genropy Headers ================ -->
        <script type="text/javascript" src="${dojolib}"
                djConfig="${djConfig}"></script>
        <script type="text/javascript">
             dojo.registerModulePath('gnr','${gnrModulePath}')
        </script>
% if dijitImport:
        <script type="text/javascript" src="${dijitImport}"></script>
% endif

% for jsname in genroJsImport:
        <script type="text/javascript" src="${jsname}"></script>
% endfor

% for customHeader in customHeaders:
        ${customHeader}
% endfor

% for jsname in js_requires:
        <script type="text/javascript" src="${jsname}"></script>
% endfor

        <style type="text/css">
            % for cssname in css_dojo:
            @import url("${cssname}");  
            % endfor
        </style>
            
        % for cssmedia, cssnames  in css_genro.items():
        <style type="text/css" media="${cssmedia}">
                % for cssname in cssnames:
            @import url("${cssname}");
                % endfor
        </style>
        % endfor
        <style type="text/css">    
            % for cssname in css_requires:
            @import url("${cssname}");
            % endfor
        </style>
        
        % for cssmedia, cssnames  in css_media_requires.items():
        <style type="text/css" media="${cssmedia}">
                % for cssname in cssnames:
            @import url("${cssname}");
                % endfor
        </style>
        % endfor
        
        <script type="text/javascript">
            var genro = new gnr.GenroClient({ page_id:'${page_id}',baseUrl:'${filename}', pageMode: '${pageMode or "legacy"}',
                                              domRootName:'mainWindow', startArgs: ${startArgs}});
        </script>