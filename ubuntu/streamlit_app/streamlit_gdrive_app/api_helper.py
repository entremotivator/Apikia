"""API Helper Module for KIE.AI API Operations"""

import requests
from unified_api import UnifiedKIEAPI, VIDEO_TEMPLATES, IMAGE_TEMPLATES
import time
import json
from typing import Optional, Dict, List


# Initialize the unified KIE.AI API client
UNIFIED_API = UnifiedKIEAPI()


class BaseAPIClient:
    """Base class for KIE.AI API operations"""
    
    def __init__(self, api_key: str):
        """
        Initialize API Client
        
        Args:
            api_key: API key for authentication
        """
        self.api_key = api_key
        self.base_url = "https://api.kie.ai/api/v1/jobs"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def create_task(self, model: str, input_params: dict, callback_url: Optional[str] = None) -> Optional[str]:
        """
        Create a generation task
        
        Args:
            model: Model name
            input_params: Input parameters dictionary
            callback_url: Optional callback URL
            
        Returns:
            Task ID or None if failed
        """
        url = f"{self.base_url}/createTask"
        
        payload = {
            "model": model,
            "input": input_params
        }
        
        if callback_url:
            payload["callBackUrl"] = callback_url
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("code") == 200:
                return result.get("data", {}).get("taskId")
            else:
                print(f"Error creating task: {result.get('msg')}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
    
    def query_task(self, task_id: str) -> Optional[Dict]:
        """
        Query task status and results
        
        Args:
            task_id: Task ID to query
            
        Returns:
            Task information dictionary or None if failed
        """
        url = f"{self.base_url}/recordInfo"
        params = {"taskId": task_id}
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("code") == 200:
                return result.get("data")
            else:
                print(f"Error querying task: {result.get('msg')}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
    
    def wait_for_completion(self, task_id: str, max_wait: int = 300, poll_interval: int = 5) -> Optional[Dict]:
        """
        Wait for task completion and return results
        
        Args:
            task_id: Task ID to wait for
            max_wait: Maximum wait time in seconds
            poll_interval: Polling interval in seconds
            
        Returns:
            Task information dictionary or None if failed/timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            task_info = self.query_task(task_id)
            
            if not task_info:
                return None
            
            state = task_info.get("state")
            
            if state == "success":
                return task_info
            elif state == "fail":
                print(f"Task failed: {task_info.get('failMsg')}")
                return task_info
            
            time.sleep(poll_interval)
        
        print("Task timeout")
        return None
    
    def get_result_urls(self, task_info: Dict) -> List[str]:
        """
        Extract result URLs from task information
        
        Args:
            task_info: Task information dictionary
            
        Returns:
            List of result URLs
        """
        if task_info.get("state") != "success":
            return []
        
        result_json_str = task_info.get("resultJson", "{}")
        
        try:
            result_json = json.loads(result_json_str)
            return result_json.get("resultUrls", [])
        except json.JSONDecodeError:
            return []


class ImageEditAPI(BaseAPIClient):
    """Handles Image Edit API operations (qwen/image-edit)"""
    
    def create_image_edit_task(self, prompt: str, image_url: str, **kwargs) -> Optional[str]:
        """
        Create an image editing task
        
        Args:
            prompt: The prompt to generate the image with
            image_url: The URL of the image to edit
            **kwargs: Additional parameters
            
        Returns:
            Task ID or None if failed
        """
        input_params = {
            "prompt": prompt,
            "image_url": image_url,
            "acceleration": kwargs.get("acceleration", "none"),
            "image_size": kwargs.get("image_size", "landscape_4_3"),
            "num_inference_steps": kwargs.get("num_inference_steps", 25),
            "guidance_scale": kwargs.get("guidance_scale", 4),
            "sync_mode": kwargs.get("sync_mode", False),
            "enable_safety_checker": kwargs.get("enable_safety_checker", True),
            "output_format": kwargs.get("output_format", "png"),
            "negative_prompt": kwargs.get("negative_prompt", "blurry, ugly")
        }
        
        if "seed" in kwargs:
            input_params["seed"] = kwargs["seed"]
        if "num_images" in kwargs:
            input_params["num_images"] = str(kwargs["num_images"])
        
        return self.create_task("qwen/image-edit", input_params, kwargs.get("callBackUrl"))


class NanoBananaAPI(BaseAPIClient):
    """Handles Nano Banana API operations (google/nano-banana)"""
    
    def create_nano_banana_task(self, prompt: str, **kwargs) -> Optional[str]:
        """
        Create a Nano Banana image generation task
        
        Args:
            prompt: The prompt for image generation
            **kwargs: Additional parameters
            
        Returns:
            Task ID or None if failed
        """
        input_params = {
            "prompt": prompt,
            "output_format": kwargs.get("output_format", "png"),
            "image_size": kwargs.get("image_size", "1:1")
        }
        
        return self.create_task("google/nano-banana", input_params, kwargs.get("callBackUrl"))


class CharacterEditAPI(BaseAPIClient):
    """Handles Character Edit API operations (ideogram/character-edit)"""
    
    def create_character_edit_task(self, prompt: str, image_url: str, mask_url: str, 
                                   reference_image_urls: List[str], **kwargs) -> Optional[str]:
        """
        Create a character editing task
        
        Args:
            prompt: The prompt to fill the masked part of the image
            image_url: The image URL to generate an image from
            mask_url: The mask URL to inpaint the image
            reference_image_urls: A set of images to use as character references
            **kwargs: Additional parameters
            
        Returns:
            Task ID or None if failed
        """
        input_params = {
            "prompt": prompt,
            "image_url": image_url,
            "mask_url": mask_url,
            "reference_image_urls": reference_image_urls,
            "rendering_speed": kwargs.get("rendering_speed", "BALANCED"),
            "style": kwargs.get("style", "AUTO"),
            "expand_prompt": kwargs.get("expand_prompt", True),
            "num_images": kwargs.get("num_images", "1")
        }
        
        if "seed" in kwargs:
            input_params["seed"] = kwargs["seed"]
        
        return self.create_task("ideogram/character-edit", input_params, kwargs.get("callBackUrl"))


# --- Unified KIE.AI API Functions ---

def generate_video(model: str, prompt: str, **kwargs):
    """
    Unified function to generate videos using KIE.AI models.
    
    Args:
        model: Video model to use (e.g., 'veo-3.1', 'runway/text-to-video', 'sora-2')
        prompt: Text prompt for video generation
        **kwargs: Additional parameters
        
    Returns:
        Dictionary with task status and information
    """
    return UNIFIED_API.generate_video(model, prompt, **kwargs)


def generate_image(model: str, prompt: str, **kwargs):
    """
    Unified function to generate images using KIE.AI models.
    
    Args:
        model: Image model to use (e.g., 'qwen/image-edit')
        prompt: Text prompt for image generation
        **kwargs: Additional parameters
        
    Returns:
        Dictionary with task status and information
    """
    return UNIFIED_API.generate_image(model, prompt, **kwargs)


def get_video_templates():
    """
    Retrieves the list of pre-made video templates.
    
    Returns:
        List of video template dictionaries
    """
    return VIDEO_TEMPLATES


def get_image_templates():
    """
    Retrieves the list of pre-made image templates.
    
    Returns:
        List of image template dictionaries
    """
    return IMAGE_TEMPLATES


def query_task(task_id: str):
    """
    Query the status of a generation task.
    
    Args:
        task_id: Task ID to query
        
    Returns:
        Task information dictionary or None
    """
    return UNIFIED_API.query_task(task_id)


def wait_for_task(task_id: str, max_wait: int = 300):
    """
    Wait for a task to complete.
    
    Args:
        task_id: Task ID to wait for
        max_wait: Maximum wait time in seconds
        
    Returns:
        Task information when complete or None
    """
    return UNIFIED_API.wait_for_completion(task_id, max_wait)
