function varargout = finalUI(varargin)
% FINALUI MATLAB code for finalUI.fig
%      FINALUI, by itself, creates a new FINALUI or raises the existing
%      singleton*.
%
%      H = FINALUI returns the handle to a new FINALUI or the handle to
%      the existing singleton*.
%
%      FINALUI('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in FINALUI.M with the given input arguments.
%
%      FINALUI('Property','Value',...) creates a new FINALUI or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before finalUI_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to finalUI_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit the above text to modify the response to help finalUI

% Last Modified by GUIDE v2.5 25-Oct-2020 00:05:45

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...how 
                   'gui_OpeningFcn', @finalUI_OpeningFcn, ...
                   'gui_OutputFcn',  @finalUI_OutputFcn, ...
                   'gui_LayoutFcn',  [] , ...
                   'gui_Callback',   []);
if nargin && ischar(varargin{1})
    gui_State.gui_Callback = str2func(varargin{1});
end

if nargout
    [varargout{1:nargout}] = gui_mainfcn(gui_State, varargin{:});
else

    gui_mainfcn(gui_State, varargin{:});
end
% End initialization code - DO NOT EDIT

function figure1_CreateFcn(varargin)



% --- Executes just before finalUI is made visible.
function finalUI_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to finalUI (see VARARGIN)

% Choose default command line output for finalUI
handles.output = hObject;

strings = seriallist;
handles.s = serial(strings(1),'BaudRate',115200, 'Terminator','CR');
handles.pulse = '10';
handles.valley = '40';
handles.on = '1';
handles.off = '4';
handles.pulse2 = '10';
handles.valley2 = '40';
handles.on2 = '1';
handles.off2 = '4';
handles.lastclicktime = clock;
handles.lastclickbutton = 0;
handles.timeinF1 = 0;
handles.timeinF2 = 0;
handles.timestop = 0;
handles.popupmenu1.String = strings;
handles.popupmenu3.String = {'1   ', '2   ', 'Both'};
handles.popupmenu5.String = {'1   ', '2   ', 'Both'};
handles.led_pin_1 = '1';
handles.led_pin_2 = '1';
handles.checkbox4.Value = true;
handles.disconnect = '0';
handles.tempsensing = '0';
handles.tempsample = '40';
handles.recording = '0';
handles.recordsample = '4';
handles.intensity = 255;
handles.rise_time = 50;
handles.fall_time = 50;
handles.samples = 1;
if exist('pulses.jpg', 'file')
  theImage = imread('pulses.jpg');
  axes(handles.axes5); % Use actual variable names from your program!
  imshow(theImage);
end
axes(handles.axes1);
handles.plotHandle = plot(handles.axes1,-65536,65536,'Marker','.','LineWidth',1,'Color',[1 0 0]);
xlim(handles.axes1,[0 handles.samples+10]);
xlabel(handles.axes1,'Time (seconds)','FontSize',14);
ylabel(handles.axes1,'Recorded ADC Value','FontSize',14);
handles.axes1.YAxis.FontSize = 13;
handles.axes1.XAxis.FontSize = 13;
% Update handles structure
guidata(hObject, handles);

% UIWAIT makes finalUI wait for user response (see UIRESUME)
% uiwait(handles.figure1);


% --- Outputs from this function are returned to the command line.
function varargout = finalUI_OutputFcn(hObject, eventdata, handles) 
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1} = handles.output;



function edit1_Callback(hObject, eventdata, handles)
% hObject    handle to edit1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
    handles.duty = get(hObject,'String');
    guidata(hObject, handles);
% Hints: get(hObject,'String') returns contents of edit1 as text
%        str2double(get(hObject,'String')) returns contents of edit1 as a double


% --- Executes during object creation, after setting all properties.
function edit1_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function edit2_Callback(hObject, eventdata, handles)
% hObject    handle to edit2 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
    handles.pulse = get(hObject,'String');
    guidata(hObject, handles);
% Hints: get(hObject,'String') returns contents of edit2 as text
%        str2double(get(hObject,'String')) returns contents of edit2 as a double


% --- Executes during object creation, after setting all properties.
function edit2_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit2 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in pushbutton1.
function pushbutton1_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
fprintf(handles.s, '%s,', handles.pulse);
fprintf(handles.s, '%s,', handles.valley);
fprintf(handles.s, '%s,',handles.on);
fprintf(handles.s, '%s,', handles.off);
fprintf(handles.s, '%s,', handles.led_pin_1);
fprintf(handles.s, '%s,', handles.disconnect);
fprintf(handles.s, '%s,', handles.tempsensing);
fprintf(handles.s, '%s,', handles.tempsample);
fprintf(handles.s, '%s,', handles.recording);
fprintf(handles.s, '%s,', handles.recordsample);
fprintf(handles.s, '%d,', handles.intensity);
fprintf(handles.s, '%d,', handles.rise_time);
fprintf(handles.s, '%d\r\n', handles.fall_time);
handles.text16.String = "STARTED F1";
if (handles.lastclickbutton ~= 0)
    elapsed = etime(clock, handles.lastclicktime);
    switch handles.lastclickbutton
        case 1
            handles.timeinF1 = handles.timeinF1 + elapsed;
        case 2
            handles.timeinF2 = handles.timeinF2 + elapsed;
        case 3
            handles.timestop = handles.timestop + elapsed;
    end
end
handles.lastclicktime = clock;
handles.lastclickbutton = 1;
guidata(hObject, handles);
% fprintf(handles.s, '%s,', '40');
% fprintf(handles.s, '%s,', handles.valley);
% fprintf(handles.s, '%s\n', handles.on);
% % fprintf(handles.s, '%s\n', handles.off);




function edit3_Callback(hObject, eventdata, handles)
% hObject    handle to edit3 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
handles.on = get(hObject,'String');
guidata(hObject, handles);
% Hints: get(hObject,'String') returns contents of edit3 as text
%        str2double(get(hObject,'String')) returns contents of edit3 as a double


% --- Executes during object creation, after setting all properties.
function edit3_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit3 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function edit4_Callback(hObject, eventdata, handles)
% hObject    handle to edit4 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
handles.off = get(hObject,'String');
guidata(hObject, handles);
% Hints: get(hObject,'String') returns contents of edit4 as text
%        str2double(get(hObject,'String')) returns contents of edit4 as a double


% --- Executes during object creation, after setting all properties.
function edit4_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit4 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end

% --- Executes on button press in togglebutton1.
% function togglebutton1_Callback(hObject, eventdata, handles)
% % hObject    handle to togglebutton1 (see GCBO)
% % eventdata  reserved - to be defined in a future version of MATLAB
% % handles    structure with handles and user data (see GUIDATA)
% if (get(hObject,'Value'))
%     fopen(handles.s);
%     guidata(hObject, handles);
% else 
%     fclose(handles.s);
%     guidata(hObject, handles);
% end
% % Hint: get(hObject,'Value') returns toggle state of togglebutton1
% --- Executes on button press in togglebutton1.
function togglebutton1_Callback(hObject, eventdata, handles)
% hObject    handle to togglebutton1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
if (get(hObject,'Value'))
    handles.s.BytesAvailableFcnMode = 'terminator';
    handles.s.BytesAvailableFcn = {@data_recieved, hObject};
    fopen(handles.s);
    guidata(hObject, handles);
else
    fclose(handles.s);
    guidata(hObject, handles);
end
% Hint: get(hObject,'Value') returns toggle state of togglebutton1

function data_recieved(obj, event, hObject)
 handles = guidata(hObject);
 out = fscanf(handles.s);
 out_size = size(out);
 c ='Connected   ';
 d ='Disconnected';
 s ='START';
 s2 = 'STOP';
 if strcmp(out(1:end-1),c) == 1
%      if out(length(out)-1) == '1'
     handles.text15.String = "CONNECTED    ";
 elseif strcmp(out(1:end-1),d) == 1
     handles.text15.String = "NOT CONNECTED";
 elseif strcmp(out(1:end-1),s) == 1
     handles.text16.String = "PULSING";
 elseif strcmp(out(1:end-1),s2) == 1
     handles.text16.String = "OFF    ";
 else
      handles.temp(handles.samples) = str2double(out);
      if handles.recording == "1"
          sampleRate = handles.recordsample;
      elseif handles.tempsensing == "1"
          sampleRate = handles.tempsample;
      end
      
      handles.time(handles.samples) = handles.samples*str2double(sampleRate)*.001;
% %     
% %     %pause(TimeInterval);
     handles.samples = handles.samples +1;
      
     if mod(handles.samples, 101)
         drawnow limitrate;
         xlim(handles.axes1,[0 handles.time(end)]);
         set(handles.plotHandle,'YData',handles.temp,'XData',handles.time);
     end
      % set(figureHandle,'Visible','on');
     
%      else
%         handles.text15.String = "NOT CONNECTED";
     %end
     %handles.text19.String = out(length(out)-3);
 end

 guidata(hObject, handles);


function edit5_Callback(hObject, eventdata, handles)
% hObject    handle to edit5 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
handles.valley = get(hObject,'String');
guidata(hObject, handles);
% Hints: get(hObject,'String') returns contents of edit5 as text
%        str2double(get(hObject,'String')) returns contents of edit5 as a double


% --- Executes during object creation, after setting all properties.
function edit5_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit5 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on selection change in popupmenu1.
function popupmenu1_Callback(hObject, eventdata, handles)
% hObject    handle to popupmenu1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns popupmenu1 contents as cell array
%        contents{get(hObject,'Value')} returns selected item from popupmenu1
if (handles.togglebutton1.Value) 
    fclose(handles.s);
    handles.togglebutton1.Value = false;
end
contents = cellstr(get(hObject,'String'));
handles.s = serial(contents{get(hObject,'Value')},'BaudRate',115200, 'Terminator','CR');
guidata(hObject, handles);

% --- Executes during object creation, after setting all properties.
function popupmenu1_CreateFcn(hObject, eventdata, handles)
% hObject    handle to popupmenu1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on selection change in popupmenu3.
function popupmenu3_Callback(hObject, eventdata, handles)
% hObject    handle to popupmenu3 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns popupmenu3 contents as cell array
%        contents{get(hObject,'Value')} returns selected item from popupmenu3
contents = cellstr(get(hObject,'String'));
if contents{get(hObject,'Value')} == '1   '
    handles.led_pin_1 = '1';
    if (handles.led_pin_2 == '1')
        set(handles.checkbox3,'Enable','on')
        set(handles.checkbox2,'Enable','on')
        set(handles.checkbox6,'Enable','on')
    end
end
if contents{get(hObject,'Value')} == '2   '
    handles.led_pin_1 = '2';
    handles.checkbox3.Value = false;
    set(handles.checkbox3,'Enable','off')
    handles.checkbox2.Value = false;
    set(handles.checkbox2,'Enable','off')
    handles.tempsensing = '0';
 %   handles.checkbox6.Value = false;
 %   set(handles.checkbox6,'Enable','off')
 %   handles.recording = '0';
end
if contents{get(hObject,'Value')} == 'Both'
    handles.led_pin_1 = '4';
    handles.checkbox3.Value = false;
    set(handles.checkbox3,'Enable','off')
    handles.checkbox2.Value = false;
    set(handles.checkbox2,'Enable','off')
    handles.tempsensing = '0';
 %   handles.checkbox6.Value = false;
 %   set(handles.checkbox6,'Enable','off')
 %   handles.recording = '0';
end
guidata(hObject, handles);

% --- Executes during object creation, after setting all properties.
function popupmenu3_CreateFcn(hObject, eventdata, handles)
% hObject    handle to popupmenu3 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end

set(findall(gcf,'-property','FontSize'),'FontSize',14)


% --- Executes on selection change in popupmenu4.
function popupmenu4_Callback(hObject, eventdata, handles)
% hObject    handle to popupmenu4 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns popupmenu4 contents as cell array
%        contents{get(hObject,'Value')} returns selected item from popupmenu4
contents = cellstr(get(hObject,'String'));
if contents{get(hObject,'Value')} == 'ON '
    handles.disconnect = '0';
end
if contents{get(hObject,'Value')} == 'OFF'
    handles.disconnect = '1';
end
guidata(hObject, handles);

% --- Executes during object creation, after setting all properties.
function popupmenu4_CreateFcn(hObject, eventdata, handles)
% hObject    handle to popupmenu4 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in togglebutton3.
function togglebutton3_Callback(hObject, eventdata, handles)
% hObject    handle to togglebutton3 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of togglebutton3
if get(hObject,'Value')
    fprintf(handles.s, '%s', 'STOP,\n');
    %handles.togglebutton3.String = "Unpause";
    
else
    fprintf(handles.s, '%s', 'STOP,\n');

end
handles.togglebutton3.String = "Pause  ";
handles.text16.String = "PAUSED   ";
if (handles.lastclickbutton ~= 0)
    elapsed = etime(clock, handles.lastclicktime);
    switch handles.lastclickbutton
        case 1
            handles.timeinF1 = handles.timeinF1 + elapsed;
        case 2
            handles.timeinF2 = handles.timeinF2 + elapsed;
        case 3
            handles.timestop = handles.timestop + elapsed;
    end
end
handles.timeinF2
handles.timestop
handles.timeinF1
handles.lastclicktime = clock;
handles.lastclickbutton = 3;
guidata(hObject, handles);



function edit6_Callback(hObject, eventdata, handles)
% hObject    handle to edit6 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit6 as text
%        str2double(get(hObject,'String')) returns contents of edit6 as a double
handles.pulse2 = get(hObject,'String');
guidata(hObject, handles);

% --- Executes during object creation, after setting all properties.
function edit6_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit6 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function edit7_Callback(hObject, eventdata, handles)
% hObject    handle to edit7 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit7 as text
%        str2double(get(hObject,'String')) returns contents of edit7 as a double
handles.on2 = get(hObject,'String');
guidata(hObject, handles);

% --- Executes during object creation, after setting all properties.
function edit7_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit7 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function edit8_Callback(hObject, eventdata, handles)
% hObject    handle to edit8 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit8 as text
%        str2double(get(hObject,'String')) returns contents of edit8 as a double
handles.off2 = get(hObject,'String');
guidata(hObject, handles);

% --- Executes during object creation, after setting all properties.
function edit8_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit8 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function edit9_Callback(hObject, eventdata, handles)
% hObject    handle to edit9 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit9 as text
%        str2double(get(hObject,'String')) returns contents of edit9 as a double
handles.valley2 = get(hObject,'String');
guidata(hObject, handles);

% --- Executes during object creation, after setting all properties.
function edit9_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit9 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in pushbutton6.
function pushbutton6_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton6 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
fprintf(handles.s, '%s,', handles.pulse2);
fprintf(handles.s, '%s,', handles.valley2);
fprintf(handles.s, '%s,',handles.on2);
fprintf(handles.s, '%s,', handles.off2);
fprintf(handles.s, '%s,', handles.led_pin_2);
fprintf(handles.s, '%s,', handles.disconnect);
fprintf(handles.s, '%s,', handles.tempsensing);
fprintf(handles.s, '%s,', handles.tempsample);
fprintf(handles.s, '%s,', handles.recording);
fprintf(handles.s, '%s,', handles.recordsample);
fprintf(handles.s, '%d,', handles.intensity);
fprintf(handles.s, '%d,', handles.rise_time);
fprintf(handles.s, '%d\n', handles.fall_time);
handles.text16.String = "STARTED F2";
if (handles.lastclickbutton ~= 0)
    elapsed = etime(clock, handles.lastclicktime);
    switch handles.lastclickbutton
        case 1
            handles.timeinF1 = handles.timeinF1 + elapsed;
        case 2
            handles.timeinF2 = handles.timeinF2 + elapsed;
        case 3
            handles.timestop = handles.timestop + elapsed;
    end
end
handles.lastclicktime = clock;
handles.lastclickbutton = 2;
guidata(hObject, handles);



function edit12_Callback(hObject, eventdata, handles)
% hObject    handle to edit12 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit12 as text
%        str2double(get(hObject,'String')) returns contents of edit12 as a double
handles.tempsample = get(hObject,'String');
guidata(hObject, handles);

% --- Executes during object creation, after setting all properties.
function edit12_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit12 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in checkbox2.
function checkbox2_Callback(hObject, eventdata, handles)
% hObject    handle to checkbox2 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of checkbox2
if get(hObject,'Value') ==  true
    handles.tempsensing = '1';
else 
    handles.tempsensing = '0';
end
    if handles.tempsensing == '1';
        handles.checkbox6.Value = false;
        set(handles.checkbox6,'Enable','off')
        handles.recording = '0';
    else 
        handles.checkbox6.Value = false;
        set(handles.checkbox6,'Enable','on')
    end
    
guidata(hObject, handles);

% --- Executes on button press in checkbox3.
function checkbox3_Callback(hObject, eventdata, handles)
% hObject    handle to checkbox3 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of checkbox3
if get(hObject,'Value') ==  true
    handles.led_pin_2 = '3';
    handles.led_pin_1 = '3';
else
    handles.led_pin_1 = '1';
    handles.led_pin_2 = '1';
end
guidata(hObject, handles);


function edit13_Callback(hObject, eventdata, handles)
% hObject    handle to edit13 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit13 as text
%        str2double(get(hObject,'String')) returns contents of edit13 as a double
handles.rise_time = round(str2double(get(hObject,'String'))/28);
guidata(hObject, handles);

% --- Executes during object creation, after setting all properties.
function edit13_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit13 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function edit14_Callback(hObject, eventdata, handles)
% hObject    handle to edit14 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit14 as text
%        str2double(get(hObject,'String')) returns contents of edit14 as a double
handles.fall_time = round(str2double(get(hObject,'String'))/28);
guidata(hObject, handles);

% --- Executes during object creation, after setting all properties.
function edit14_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit14 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in checkbox4.
function checkbox4_Callback(hObject, eventdata, handles)
% hObject    handle to checkbox4 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of checkbox4
if get(hObject,'Value') == true
    handles.disconnect = '0';
end
if get(hObject,'Value') == false
    handles.disconnect = '1';
end
guidata(hObject, handles);



function edit15_Callback(hObject, eventdata, handles)
% hObject    handle to edit15 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit15 as text
%        str2double(get(hObject,'String')) returns contents of edit15 as a double
handles.intensity = round(str2double(get(hObject,'String'))/2.8*255);
guidata(hObject, handles);

% --- Executes during object creation, after setting all properties.
function edit15_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit15 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on selection change in popupmenu5.
function popupmenu5_Callback(hObject, eventdata, handles)
% hObject    handle to popupmenu5 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns popupmenu5 contents as cell array
%        contents{get(hObject,'Value')} returns selected item from popupmenu5
contents = cellstr(get(hObject,'String'));
if contents{get(hObject,'Value')} == '1   '
    handles.led_pin_2 = '1';
    if (handles.led_pin_1 == '1')
        set(handles.checkbox3,'Enable','on')
        set(handles.checkbox2,'Enable','on')
        set(handles.checkbox6,'Enable','on')
    end
end
if contents{get(hObject,'Value')} == '2   '
    handles.led_pin_2 = '2';
    handles.checkbox3.Value = false;
    set(handles.checkbox3,'Enable','off')
    handles.checkbox2.Value = false;
    set(handles.checkbox2,'Enable','off')
    handles.tempsensing = '0';
%    handles.checkbox6.Value = false;
%    set(handles.checkbox6,'Enable','off')
%    handles.recording = '0';
end
if contents{get(hObject,'Value')} == 'Both'
    handles.led_pin_2 = '4';
    handles.checkbox3.Value = false;
    set(handles.checkbox3,'Enable','off')
    handles.checkbox2.Value = false;
    set(handles.checkbox2,'Enable','off')
    handles.tempsensing = '0';
%    handles.checkbox6.Value = false;
%    set(handles.checkbox6,'Enable','off')
%    handles.recording = '0';
end
guidata(hObject, handles);

% --- Executes during object creation, after setting all properties.
function popupmenu5_CreateFcn(hObject, eventdata, handles)
% hObject    handle to popupmenu5 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes when user attempts to close figure1.
function figure1_CloseRequestFcn(hObject, eventdata, handles)
% hObject    handle to figure1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% Hint: delete(hObject) closes the figure
delete(hObject);


% --- Executes on button press in pushbutton7.
function pushbutton7_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton7 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
data = handles.temp;
save('Tempdata','data')
[file,path] = uiputfile('temperature_recording.fig');
fullpath = fullfile(path, file);
fignew = figure('Visible','off'); % Invisible figure
newAxes = copyobj(handles.axes1,fignew); % Copy the appropriate axes
set(newAxes,'Position',get(groot,'DefaultAxesPosition')); % The original position is copied too, so adjust it.
set(fignew,'CreateFcn','set(gcbf,''Visible'',''on'')'); % Make it visible upon loading
savefig(fignew,fullpath);
delete(fignew);



function edit20_Callback(hObject, eventdata, handles)
% hObject    handle to edit12 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit12 as text
%        str2double(get(hObject,'String')) returns contents of edit12 as a double
handles.recordsample = get(hObject,'String');
guidata(hObject, handles);


% --- Executes during object creation, after setting all properties.
function edit20_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit20 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in checkbox6.
function checkbox6_Callback(hObject, eventdata, handles)
% hObject    handle to checkbox2 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of checkbox2
if get(hObject,'Value') ==  true
    handles.recording = '1';
else 
    handles.recording = '0';
end
    if handles.recording == '1';
        handles.checkbox2.Value = false;
        set(handles.checkbox2,'Enable','off')
        handles.tempsensing = '0';
        handles.checkbox3.Value = false;
        set(handles.checkbox3,'Enable','off')
    else 
        handles.checkbox2.Value = false;
        set(handles.checkbox2,'Enable','on')
        handles.checkbox3.Value = false;
        set(handles.checkbox3,'Enable','on')
    end
    
guidata(hObject, handles);


% --------------------------------------------------------------------
