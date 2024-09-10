import sys
from ids_peak import ids_peak as peak
from ids_peak import ids_peak_ipl_extension


class IDSCamera:
    
    def __init__(self):
        peak.Library.Initialize()
        self.m_device = None
        self.m_dataStream = None
        self.m_node_map_remote_device = None

    def open_camera(self):
        try:
            # Create instance of the device manager
            device_manager = peak.DeviceManager.Instance()

            # Update the device manager
            device_manager.Update()

            # Return if no device was found
            if device_manager.Devices().empty():
                return False

            # open the first openable device in the device manager's device list
            device_count = device_manager.Devices().size()
            for i in range(device_count):
                if device_manager.Devices()[i].IsOpenable():
                    self.m_device = device_manager.Devices()[i].OpenDevice(peak.DeviceAccessType_Control)
        
                    # Get NodeMap of the RemoteDevice for all accesses to the GenICam NodeMap tree
                    self.m_node_map_remote_device = self.m_device.RemoteDevice().NodeMaps()[0]

                    return True
        except Exception as e:
            # ...
            str_error = str(e)

        return False
    
    def mode_setting(self):
        try:
            self.m_node_map_remote_device.FindNode("UserSetSelector").SetCurrentEntry("Default")
            self.m_node_map_remote_device.FindNode("UserSetLoad").Execute()
            self.m_node_map_remote_device.FindNode("UserSetLoad").WaitUntilDone()
            
            return True
        except Exception as e:
            # ...
            str_error = str(e)

        return False

    def prepare_acquisition(self):

        try:
            data_streams = self.m_device.DataStreams()
            if data_streams.empty():
                # no data streams available
                return False
            
            self.mode_setting()
            self.m_dataStream = self.m_device.DataStreams()[0].OpenDataStream()

            return True
        except Exception as e:
            # ...
            str_error = str(e)

        return False

    
    def set_roi(self, x, y, width, height):
        try:
            # Get the minimum ROI and set it. After that there are no size restrictions anymore
            x_min = self.m_node_map_remote_device.FindNode("OffsetX").Minimum()
            y_min = self.m_node_map_remote_device.FindNode("OffsetY").Minimum()
            w_min = self.m_node_map_remote_device.FindNode("Width").Minimum()
            h_min = self.m_node_map_remote_device.FindNode("Height").Minimum()

            self.m_node_map_remote_device.FindNode("OffsetX").SetValue(x_min)
            self.m_node_map_remote_device.FindNode("OffsetY").SetValue(y_min)
            self.m_node_map_remote_device.FindNode("Width").SetValue(w_min)
            self.m_node_map_remote_device.FindNode("Height").SetValue(h_min)

            # Get the maximum ROI values
            x_max = self.m_node_map_remote_device.FindNode("OffsetX").Maximum()
            y_max = self.m_node_map_remote_device.FindNode("OffsetY").Maximum()
            w_max = self.m_node_map_remote_device.FindNode("Width").Maximum()
            h_max = self.m_node_map_remote_device.FindNode("Height").Maximum()

            if (x < x_min) or (y < y_min) or (x > x_max) or (y > y_max):
                return False
            elif (width < w_min) or (height < h_min) or ((x + width) > w_max) or ((y + height) > h_max):
                return False
            else:
                # Now, set final AOI
                self.m_node_map_remote_device.FindNode("OffsetX").SetValue(x)
                self.m_node_map_remote_device.FindNode("OffsetY").SetValue(y)
                self.m_node_map_remote_device.FindNode("Width").SetValue(width)
                self.m_node_map_remote_device.FindNode("Height").SetValue(height)

                return True
        except Exception as e:
            # ...
            str_error = str(e)

        return False

    def config_image(self):
        try:
            # Nodemap for accessing GenICam nodes
            print(f'Pre exposureTime: {self.m_node_map_remote_device.FindNode('ExposureTime').Value()}')
            self.m_node_map_remote_device.FindNode("ExposureTime").SetValue(38000)
            print(f'Post exposureTime: {self.m_node_map_remote_device.FindNode('ExposureTime').Value()}')
            
            self.m_node_map_remote_device.FindNode("GainSelector").SetCurrentEntry("AnalogAll")
            print(f'Pre AnalogGain: {self.m_node_map_remote_device.FindNode('Gain').Value()}')
            self.m_node_map_remote_device.FindNode("Gain").SetValue(1.0)
            print(f'Post AnalogGain: {self.m_node_map_remote_device.FindNode('Gain').Value()}')
            
            self.m_node_map_remote_device.FindNode("GainSelector").SetCurrentEntry("DigitalAll")
            print(f'Pre DigitalAll: {self.m_node_map_remote_device.FindNode('Gain').Value()}')
            self.m_node_map_remote_device.FindNode("Gain").SetValue(1.0)
            print(f'Post DigitalAll: {self.m_node_map_remote_device.FindNode('Gain').Value()}')
            
            print(f'Pre FPS: {self.m_node_map_remote_device.FindNode('AcquisitionFrameRate').Value()}')
            self.m_node_map_remote_device.FindNode("AcquisitionFrameRate").SetValue(25)
            print(f'Post FPS: {self.m_node_map_remote_device.FindNode('AcquisitionFrameRate').Value()}')
            
            return True
        except Exception as e:
            # ...
            str_error = str(e)
        
        return False
        
    def alloc_and_announce_buffers(self):
        try:
            if self.m_dataStream:
                # Flush queue and prepare all buffers for revoking
                self.m_dataStream.Flush(peak.DataStreamFlushMode_DiscardAll)

                # Clear all old buffers
                for buffer in self.m_dataStream.AnnouncedBuffers():
                    self.m_dataStream.RevokeBuffer(buffer)

                payload_size = self.m_node_map_remote_device.FindNode("PayloadSize").Value()

                # Get number of minimum required buffers
                num_buffers_min_required = self.m_dataStream.NumBuffersAnnouncedMinRequired()

                # Alloc buffers
                for count in range(num_buffers_min_required):
                    buffer = self.m_dataStream.AllocAndAnnounceBuffer(payload_size)
                    self.m_dataStream.QueueBuffer(buffer)

                return True
        except Exception as e:
            # ...
            str_error = str(e)

        return False


    def start_acquisition(self):
        try:
            self.m_dataStream.StartAcquisition(peak.AcquisitionStartMode_Default, peak.DataStream.INFINITE_NUMBER)
            self.m_node_map_remote_device.FindNode("TLParamsLocked").SetValue(1)
            self.m_node_map_remote_device.FindNode("AcquisitionStart").Execute()
            self.m_node_map_remote_device.FindNode("AcquisitionStart").WaitUntilDone()
        
            return True
        except Exception as e:
            # ...
            str_error = str(e)

        return False
    
    def stop_acquisition(self):
        try:
            self.m_node_map_remote_device.FindNode("AcquisitionStop").Execute()
            self.m_node_map_remote_device.FindNode("AcquisitionStop").WaitUntilDone()
            self.m_dataStream.StopAcquisition(peak.AcquisitionStopMode_Default)
            self.m_dataStream.Flush(peak.DataStreamFlushMode_DiscardAll)
            # Clear all old buffers
            for buffer in self.m_dataStream.AnnouncedBuffers():
                self.m_dataStream.RevokeBuffer(buffer)
                
            self.m_node_map_remote_device.FindNode("TLParamsLocked").SetValue(0)
        
            return True
        except Exception as e:
            # ...
            str_error = str(e)

        return False

    def enable_polarize_angle(self):
        try:
            component_selector_node = self.m_node_map_remote_device.FindNode("ComponentSelector")
            component_enable_node = self.m_node_map_remote_device.FindNode("ComponentEnable")
            # print(component_selector_node.Value())
            if component_selector_node and component_enable_node:
                self.m_node_map_remote_device.FindNode('ComponentSelector').SetCurrentEntry('PolarizationAngle')
                self.m_node_map_remote_device.FindNode('ComponentEnable').SetValue(True)
                print("PolarizationAngle component enabled")
                return True
            else:
                print("ComponentSelector or ComponentEnable node is not available.")
                return False
        except Exception as e:
            print(f"Failed to enable PolarizationAngle: {e}")
        return False
            
    def enable_intensity(self):
        try:
            component_selector_node = self.m_node_map_remote_device.FindNode("ComponentSelector")
            component_enable_node = self.m_node_map_remote_device.FindNode("ComponentEnable")
            if component_selector_node and component_enable_node:
                component_selector_node.SetCurrentEntry("Intensity")
                component_enable_node.SetValue(True)
                print("Intensity component enabled")
                return True
            else:
                print("ComponentSelector or ComponentEnable node is not available.")
                return False
        except Exception as e:
            print(f"Failed to enable Intensity: {e}")
        return False
    
    def capture_frame(self):
        try:
            buffer = self.m_dataStream.WaitForFinishedBuffer(1000)
            frame = ids_peak_ipl_extension.BufferToImage(buffer).get_numpy()
            self.m_dataStream.QueueBuffer(buffer)
            return frame
        except Exception as e:
            print(f"Exception: {e}")
            return None

    def dispose(self):
        peak.Library.Close()
        