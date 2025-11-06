"""
Unified KIE.AI API Abstraction Layer
This module provides a single interface for all KIE.AI video and image generation models.
Reference: https://docs.kie.ai/
"""

import os
import requests
import time
import json
import streamlit as st
from typing import Optional, Dict, List

# --- Configuration ---

KIE_AI_BASE_URL = "https://api.kie.ai/api/v1/jobs"
KIE_AI_API_KEY = os.getenv("KIE_AI_API_KEY")


class UnifiedKIEAPI:
    """
    A unified API abstraction layer for KIE.AI video and image generation models.
    Supports multiple video generation models through a single interface.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Unified KIE.AI API client.
        
        Args:
            api_key: KIE.AI API key. If not provided, uses KIE_AI_API_KEY environment variable.
        """
        self.api_key = api_key or KIE_AI_API_KEY
        
        if not self.api_key:
            st.warning("⚠️ KIE.AI API Key not configured. Please set KIE_AI_API_KEY environment variable.")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    # --- Core API Methods ---
    
    def create_task(self, model: str, input_params: dict, callback_url: Optional[str] = None) -> Optional[str]:
        """
        Create a generation task with KIE.AI API.
        
        Args:
            model: Model identifier (e.g., 'veo-3.1', 'runway/text-to-video', 'sora-2')
            input_params: Input parameters for the model
            callback_url: Optional callback URL for task completion
            
        Returns:
            Task ID if successful, None otherwise
        """
        if not self.api_key:
            return None
        
        url = f"{KIE_AI_BASE_URL}/createTask"
        
        payload = {
            "model": model,
            "input": input_params
        }
        
        if callback_url:
            payload["callBackUrl"] = callback_url
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("code") == 200:
                return result.get("data", {}).get("taskId")
            else:
                st.error(f"❌ Task creation failed: {result.get('msg')}")
                return None
        
        except requests.exceptions.RequestException as e:
            st.error(f"❌ API request failed: {e}")
            return None
    
    def query_task(self, task_id: str) -> Optional[Dict]:
        """
        Query the status and results of a generation task.
        
        Args:
            task_id: Task ID to query
            
        Returns:
            Task information dictionary or None if failed
        """
        if not self.api_key:
            return None
        
        url = f"{KIE_AI_BASE_URL}/recordInfo"
        params = {"taskId": task_id}
        
        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("code") == 200:
                return result.get("data")
            else:
                st.error(f"❌ Query failed: {result.get('msg')}")
                return None
        
        except requests.exceptions.RequestException as e:
            st.error(f"❌ API request failed: {e}")
            return None
    
    def wait_for_completion(self, task_id: str, max_wait: int = 300, poll_interval: int = 5) -> Optional[Dict]:
        """
        Wait for a task to complete and return results.
        
        Args:
            task_id: Task ID to wait for
            max_wait: Maximum wait time in seconds
            poll_interval: Polling interval in seconds
            
        Returns:
            Task information when complete, or None if timeout/failed
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
                st.error(f"❌ Task failed: {task_info.get('failMsg')}")
                return task_info
            
            time.sleep(poll_interval)
        
        st.warning("⏱️ Task timeout - still processing")
        return None
    
    def get_result_urls(self, task_info: Dict) -> List[str]:
        """
        Extract result URLs from task information.
        
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
    
    # --- Video Generation Methods ---
    
    def generate_video(self, model: str, prompt: str, **kwargs) -> Dict:
        """
        Generate a video using KIE.AI video models.
        
        Args:
            model: Video model to use (e.g., 'veo-3.1', 'runway/text-to-video', 'sora-2')
            prompt: Text prompt for video generation
            **kwargs: Additional parameters (duration, aspect_ratio, etc.)
            
        Returns:
            Dictionary with task status and information
        """
        input_params = {
            "prompt": prompt,
            "duration": kwargs.get("duration", 5),
            "aspect_ratio": kwargs.get("aspect_ratio", "16:9")
        }
        
        # Add optional parameters
        if "quality" in kwargs:
            input_params["quality"] = kwargs["quality"]
        if "style" in kwargs:
            input_params["style"] = kwargs["style"]
        if "image_url" in kwargs:
            input_params["image_url"] = kwargs["image_url"]
        
        task_id = self.create_task(model, input_params, kwargs.get("callback_url"))
        
        if not task_id:
            return {"error": "Failed to create task"}
        
        return {
            "status": "pending",
            "task_id": task_id,
            "model": model,
            "message": f"✅ Video generation started with model: {model}"
        }
    
    def generate_image(self, model: str, prompt: str, **kwargs) -> Dict:
        """
        Generate an image using KIE.AI image models.
        
        Args:
            model: Image model to use (e.g., 'qwen/image-edit')
            prompt: Text prompt for image generation
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with task status and information
        """
        input_params = {
            "prompt": prompt,
            "image_size": kwargs.get("image_size", "landscape_16_9"),
            "num_images": kwargs.get("num_images", "1"),
            "output_format": kwargs.get("output_format", "png")
        }
        
        # Add optional parameters
        if "image_url" in kwargs:
            input_params["image_url"] = kwargs["image_url"]
        if "acceleration" in kwargs:
            input_params["acceleration"] = kwargs["acceleration"]
        if "guidance_scale" in kwargs:
            input_params["guidance_scale"] = kwargs["guidance_scale"]
        
        task_id = self.create_task(model, input_params, kwargs.get("callback_url"))
        
        if not task_id:
            return {"error": "Failed to create task"}
        
        return {
            "status": "pending",
            "task_id": task_id,
            "model": model,
            "message": f"✅ Image generation started with model: {model}"
        }


# --- Pre-made Video Templates ---

VIDEO_TEMPLATES = [
    # --- Nature & Landscapes (15 templates) ---
    {
        "id": "veo_nature_1",
        "name": "Epic Mountain Sunrise",
        "model": "veo-3.1",
        "prompt": "A breathtaking, wide-angle shot of a snow-capped mountain range at sunrise, cinematic lighting, 4K, golden hour light rays breaking through clouds, dramatic sky with pink and orange hues, professional color grading, film grain texture",
        "duration": 6,
        "description": "Majestic mountain landscape with stunning sunrise colors",
        "category": "Nature"
    },
    {
        "id": "veo_nature_2",
        "name": "Ocean Wave Crash Slow Motion",
        "model": "veo-3.1",
        "prompt": "Extreme slow-motion shot of a massive ocean wave crashing on a rocky shore, water droplets frozen mid-air, dramatic lighting, cinematic depth of field, 8K quality, turquoise water, white foam spray, professional cinematography",
        "duration": 5,
        "description": "Stunning slow-motion ocean wave footage",
        "category": "Nature"
    },
    {
        "id": "veo_nature_3",
        "name": "Misty Forest Walk",
        "model": "veo-3.1",
        "prompt": "A serene, steady camera movement through a misty forest at dawn, sunlight filtering through tall trees, birds chirping, peaceful atmosphere, cinematic color grading, soft focus, ethereal mood, moss-covered ground, volumetric lighting",
        "duration": 7,
        "description": "Peaceful forest scene with atmospheric mist",
        "category": "Nature"
    },
    {
        "id": "veo_nature_4",
        "name": "Desert Sandstorm Epic",
        "model": "veo-3.1",
        "prompt": "Epic wide shot of a massive sandstorm approaching across desert dunes, dramatic sky with dark clouds, swirling sand particles, cinematic scale, intense atmosphere, 4K quality, golden sand, ominous mood, professional cinematography",
        "duration": 5,
        "description": "Dramatic desert sandstorm approaching",
        "category": "Nature"
    },
    {
        "id": "veo_nature_5",
        "name": "Northern Lights Dance",
        "model": "veo-3.1",
        "prompt": "Time-lapse style aurora borealis dancing across the night sky over a frozen lake, vibrant greens and purples, stars visible, magical atmosphere, ultra HD, reflections on ice, cinematic quality, ethereal beauty",
        "duration": 6,
        "description": "Mesmerizing aurora borealis display",
        "category": "Nature"
    },
    {
        "id": "veo_nature_6",
        "name": "Underwater Coral Reef",
        "model": "veo-3.1",
        "prompt": "Smooth underwater camera glide through a vibrant coral reef, tropical fish swimming, sunlight rays penetrating water, crystal clear visibility, documentary style, 4K, colorful marine life, peaceful atmosphere, professional underwater cinematography",
        "duration": 7,
        "description": "Beautiful underwater coral reef exploration",
        "category": "Nature"
    },
    {
        "id": "veo_nature_7",
        "name": "Waterfall Cascade",
        "model": "veo-3.1",
        "prompt": "Majestic waterfall cascading down rocky cliffs, mist rising, rainbow visible in spray, lush green vegetation, cinematic wide shot, 4K quality, powerful water flow, dramatic natural beauty, professional nature cinematography",
        "duration": 6,
        "description": "Powerful waterfall with rainbow mist",
        "category": "Nature"
    },
    {
        "id": "veo_nature_8",
        "name": "Cherry Blossom Spring",
        "model": "veo-3.1",
        "prompt": "Gentle breeze blowing through cherry blossom trees in full bloom, pink petals falling like snow, soft natural lighting, peaceful Japanese garden, cinematic beauty, 4K, serene atmosphere, spring season, romantic mood",
        "duration": 6,
        "description": "Romantic cherry blossom scene",
        "category": "Nature"
    },
    {
        "id": "veo_nature_9",
        "name": "Lightning Storm",
        "model": "veo-3.1",
        "prompt": "Dramatic lightning strikes illuminating dark storm clouds, multiple bolts across sky, powerful natural phenomenon, cinematic wide shot, 4K quality, intense atmosphere, purple and blue tones, professional storm cinematography",
        "duration": 5,
        "description": "Intense lightning storm footage",
        "category": "Nature"
    },
    {
        "id": "veo_nature_10",
        "name": "Autumn Forest Colors",
        "model": "veo-3.1",
        "prompt": "Camera gliding through autumn forest with vibrant red, orange, and yellow leaves, golden hour lighting, leaves falling gently, cinematic color grading, 4K, peaceful atmosphere, seasonal beauty, professional nature videography",
        "duration": 7,
        "description": "Vibrant autumn forest colors",
        "category": "Nature"
    },
    {
        "id": "sora_nature_1",
        "name": "Wildlife Safari",
        "model": "sora-2",
        "prompt": "African savanna at golden hour, elephants walking in distance, acacia trees silhouetted against orange sky, cinematic wildlife documentary style, 4K, natural behavior, peaceful atmosphere, professional wildlife cinematography",
        "duration": 8,
        "description": "Authentic African wildlife scene",
        "category": "Nature"
    },
    {
        "id": "sora_nature_2",
        "name": "Mountain Lake Reflection",
        "model": "sora-2",
        "prompt": "Perfectly still mountain lake reflecting snow-capped peaks, mirror-like water surface, sunrise colors, cinematic wide shot, 4K quality, serene atmosphere, natural beauty, professional landscape cinematography",
        "duration": 7,
        "description": "Stunning mountain lake reflection",
        "category": "Nature"
    },
    {
        "id": "sora_nature_3",
        "name": "Rainforest Canopy",
        "model": "sora-2",
        "prompt": "Drone shot rising through dense rainforest canopy, exotic birds flying, mist in air, lush green vegetation, cinematic movement, 4K, tropical atmosphere, biodiversity, professional nature documentary style",
        "duration": 8,
        "description": "Immersive rainforest canopy exploration",
        "category": "Nature"
    },
    {
        "id": "sora_nature_4",
        "name": "Glacier Ice Cave",
        "model": "sora-2",
        "prompt": "Inside a blue ice cave in glacier, light filtering through ice walls, crystalline structures, ethereal blue glow, cinematic beauty, 4K, frozen wonderland, unique natural formation, professional cinematography",
        "duration": 7,
        "description": "Magical glacier ice cave interior",
        "category": "Nature"
    },
    {
        "id": "sora_nature_5",
        "name": "Volcanic Eruption",
        "model": "sora-2",
        "prompt": "Active volcano erupting with lava flowing, dramatic night scene, glowing molten rock, smoke and ash, cinematic power, 4K quality, intense natural phenomenon, orange and red tones, professional documentary cinematography",
        "duration": 8,
        "description": "Powerful volcanic eruption at night",
        "category": "Nature"
    },
    
    # --- Urban & Cityscapes (12 templates) ---
    {
        "id": "veo_urban_1",
        "name": "Neon Cyberpunk City",
        "model": "veo-3.1",
        "prompt": "A hyper-realistic, fast-paced fly-through of a futuristic city with neon lights and flying vehicles, cyberpunk style, rain-soaked streets, holographic billboards, dramatic lighting, cinematic quality, 4K, blade runner aesthetic",
        "duration": 5,
        "description": "Futuristic cyberpunk cityscape",
        "category": "Urban"
    },
    {
        "id": "veo_urban_2",
        "name": "City Night Drone",
        "model": "veo-3.1",
        "prompt": "Aerial drone footage of a bustling city at night, car light trails, illuminated buildings, smooth camera movement, professional cinematography, 4K resolution, urban energy, modern architecture, cinematic color grading",
        "duration": 6,
        "description": "Dynamic night city aerial view",
        "category": "Urban"
    },
    {
        "id": "veo_urban_3",
        "name": "Tokyo Street Crossing",
        "model": "veo-3.1",
        "prompt": "Busy Tokyo intersection with crowds crossing, neon signs, traffic lights, urban energy, cinematic street photography style, 4K, vibrant colors, modern Japan, professional videography, dynamic composition",
        "duration": 5,
        "description": "Energetic Tokyo street scene",
        "category": "Urban"
    },
    {
        "id": "veo_urban_4",
        "name": "New York Skyline Sunset",
        "model": "veo-3.1",
        "prompt": "Manhattan skyline at sunset, golden hour lighting, skyscrapers silhouetted, Hudson River reflecting colors, cinematic wide shot, 4K quality, iconic cityscape, professional architectural cinematography",
        "duration": 6,
        "description": "Iconic NYC skyline at golden hour",
        "category": "Urban"
    },
    {
        "id": "runway_urban_1",
        "name": "Urban Street Art",
        "model": "runway/text-to-video",
        "prompt": "Camera sliding along colorful street art murals, vibrant graffiti, urban culture, artistic expression, cinematic movement, 4K, creative atmosphere, modern street art, professional videography",
        "duration": 7,
        "description": "Vibrant urban street art showcase",
        "category": "Urban"
    },
    {
        "id": "runway_urban_2",
        "name": "Modern Architecture",
        "model": "runway/text-to-video",
        "prompt": "Sleek modern building with glass facade, geometric patterns, reflections, minimalist design, cinematic architectural photography, 4K, clean lines, contemporary style, professional cinematography",
        "duration": 7,
        "description": "Contemporary architectural showcase",
        "category": "Urban"
    },
    {
        "id": "sora_urban_1",
        "name": "Subway Station Rush",
        "model": "sora-2",
        "prompt": "Busy subway station during rush hour, people moving, trains arriving, urban commute, cinematic documentary style, 4K, city life, dynamic movement, professional videography",
        "duration": 8,
        "description": "Dynamic subway rush hour scene",
        "category": "Urban"
    },
    {
        "id": "sora_urban_2",
        "name": "Rooftop City View",
        "model": "sora-2",
        "prompt": "Rooftop terrace overlooking city at dusk, lights turning on across skyline, transition from day to night, cinematic time-lapse style, 4K, urban beauty, professional cinematography",
        "duration": 9,
        "description": "Beautiful rooftop city transition",
        "category": "Urban"
    },
    {
        "id": "sora_urban_3",
        "name": "Historic European Street",
        "model": "sora-2",
        "prompt": "Charming cobblestone street in historic European city, old architecture, cafe tables, warm lighting, romantic atmosphere, cinematic travel style, 4K, cultural heritage, professional videography",
        "duration": 8,
        "description": "Romantic European street scene",
        "category": "Urban"
    },
    {
        "id": "sora_urban_4",
        "name": "Dubai Skyline Night",
        "model": "sora-2",
        "prompt": "Dubai skyline at night with Burj Khalifa, illuminated skyscrapers, luxury cityscape, cinematic aerial view, 4K, modern architecture, professional cinematography, futuristic atmosphere",
        "duration": 8,
        "description": "Luxurious Dubai night skyline",
        "category": "Urban"
    },
    {
        "id": "sora_urban_5",
        "name": "Market Street Bustle",
        "model": "sora-2",
        "prompt": "Vibrant street market with vendors, colorful produce, people shopping, cultural atmosphere, cinematic documentary style, 4K, authentic local life, professional videography",
        "duration": 9,
        "description": "Lively street market atmosphere",
        "category": "Urban"
    },
    {
        "id": "sora_urban_6",
        "name": "Bridge Traffic Time-lapse",
        "model": "sora-2",
        "prompt": "Time-lapse of traffic flowing across city bridge, light trails, urban movement, cinematic style, 4K, dynamic energy, professional cinematography, modern infrastructure",
        "duration": 7,
        "description": "Dynamic bridge traffic flow",
        "category": "Urban"
    },
    
    # --- Sci-Fi & Fantasy (10 templates) ---
    {
        "id": "veo_scifi_1",
        "name": "Space Station Orbit",
        "model": "veo-3.1",
        "prompt": "Massive space station orbiting Earth, stars in background, sci-fi architecture, cinematic space scene, 4K, futuristic technology, professional VFX quality, realistic physics, dramatic lighting",
        "duration": 6,
        "description": "Epic space station orbital view",
        "category": "Sci-Fi"
    },
    {
        "id": "veo_scifi_2",
        "name": "Alien Planet Landscape",
        "model": "veo-3.1",
        "prompt": "Alien planet surface with strange rock formations, multiple moons in sky, exotic atmosphere, cinematic sci-fi style, 4K, otherworldly beauty, professional VFX, imaginative landscape",
        "duration": 6,
        "description": "Mysterious alien planet terrain",
        "category": "Sci-Fi"
    },
    {
        "id": "veo_scifi_3",
        "name": "Holographic Interface",
        "model": "veo-3.1",
        "prompt": "Futuristic holographic user interface with floating screens, data visualization, neon blue glow, high-tech atmosphere, cinematic sci-fi style, 4K, advanced technology, professional VFX",
        "duration": 5,
        "description": "Advanced holographic technology",
        "category": "Sci-Fi"
    },
    {
        "id": "sora_scifi_1",
        "name": "Robot Assembly Line",
        "model": "sora-2",
        "prompt": "Futuristic factory with robots assembling advanced technology, automated systems, cinematic sci-fi industrial style, 4K, mechanical precision, professional cinematography, high-tech atmosphere",
        "duration": 8,
        "description": "Automated futuristic factory",
        "category": "Sci-Fi"
    },
    {
        "id": "sora_scifi_2",
        "name": "Time Portal Opening",
        "model": "sora-2",
        "prompt": "Swirling time portal opening with energy effects, blue and purple light, sci-fi VFX, cinematic quality, 4K, mysterious atmosphere, professional visual effects, dramatic reveal",
        "duration": 7,
        "description": "Dramatic time portal activation",
        "category": "Sci-Fi"
    },
    {
        "id": "sora_fantasy_1",
        "name": "Magic Forest Enchanted",
        "model": "sora-2",
        "prompt": "Enchanted forest with glowing mushrooms, fairy lights, magical atmosphere, fantasy style, cinematic beauty, 4K, ethereal mood, professional cinematography, mystical environment",
        "duration": 8,
        "description": "Magical enchanted forest scene",
        "category": "Fantasy"
    },
    {
        "id": "sora_fantasy_2",
        "name": "Dragon Flight",
        "model": "sora-2",
        "prompt": "Majestic dragon flying through clouds, scales glistening, fantasy creature, cinematic epic style, 4K, powerful wings, professional VFX, dramatic sky, mythical beauty",
        "duration": 8,
        "description": "Epic dragon flight sequence",
        "category": "Fantasy"
    },
    {
        "id": "sora_fantasy_3",
        "name": "Crystal Cave Magic",
        "model": "sora-2",
        "prompt": "Cave filled with glowing crystals, magical energy, fantasy atmosphere, cinematic lighting, 4K, ethereal beauty, professional cinematography, mystical environment",
        "duration": 7,
        "description": "Magical glowing crystal cave",
        "category": "Fantasy"
    },
    {
        "id": "sora_fantasy_4",
        "name": "Wizard Spell Casting",
        "model": "sora-2",
        "prompt": "Wizard casting powerful spell with magical effects, glowing runes, fantasy magic, cinematic VFX, 4K, dramatic lighting, professional visual effects, mystical atmosphere",
        "duration": 8,
        "description": "Dramatic spell casting scene",
        "category": "Fantasy"
    },
    {
        "id": "sora_fantasy_5",
        "name": "Floating Islands Sky",
        "model": "sora-2",
        "prompt": "Floating islands in sky connected by bridges, waterfalls cascading down, fantasy world, cinematic epic style, 4K, magical atmosphere, professional cinematography, imaginative landscape",
        "duration": 9,
        "description": "Fantastical floating islands",
        "category": "Fantasy"
    },
    
    # --- Product & Commercial (10 templates) ---
    {
        "id": "runway_product_1",
        "name": "Luxury Watch Showcase",
        "model": "runway/text-to-video",
        "prompt": "A sleek, slow-motion shot of a luxury watch rotating in mid-air against a dark, elegant background with subtle spotlight, showing intricate details, premium feel, cinematic commercial style, 4K, high-end product photography",
        "duration": 8,
        "description": "High-fidelity luxury product demonstration",
        "category": "Product"
    },
    {
        "id": "runway_product_2",
        "name": "Smartphone Advertisement",
        "model": "runway/text-to-video",
        "prompt": "Dynamic advertisement for a new smartphone, quick cuts, close-ups of screen and features, abstract background with flowing lines, energetic music sync, 4K, modern tech commercial, professional videography",
        "duration": 8,
        "description": "Energetic smartphone commercial",
        "category": "Product"
    },
    {
        "id": "runway_product_3",
        "name": "Cosmetics Product Shot",
        "model": "runway/text-to-video",
        "prompt": "Elegant cosmetics product, perhaps lipstick or perfume, with soft lighting, gentle splashes of liquid, luxurious atmosphere, pastel colors, high-end commercial style, 4K, beauty product advertisement",
        "duration": 8,
        "description": "Sophisticated beauty product video",
        "category": "Product"
    },
    {
        "id": "runway_product_4",
        "name": "Automotive Cinematic",
        "model": "runway/text-to-video",
        "prompt": "Cinematic shot of a sports car driving on a scenic road at sunset, engine roar, sleek design highlighted, professional cinematography, 4K, automotive commercial, dramatic lighting, epic landscape",
        "duration": 8,
        "description": "Dramatic sports car commercial",
        "category": "Product"
    },
    {
        "id": "sora_product_1",
        "name": "Home Appliance Demo",
        "model": "sora-2",
        "prompt": "Clean, modern kitchen setting with a new home appliance being demonstrated, sleek design, user-friendly interface, bright lighting, cinematic product demonstration style, 4K, household technology, professional videography",
        "duration": 9,
        "description": "Modern home appliance showcase",
        "category": "Product"
    },
    {
        "id": "sora_product_2",
        "name": "Beverage Commercial",
        "model": "sora-2",
        "prompt": "Refreshing beverage being poured, condensation on glass, vibrant colors, appetizing look, product close-up, studio lighting, commercial style, 4K, drinks advertisement, exciting atmosphere",
        "duration": 7,
        "description": "Appetizing beverage advertisement",
        "category": "Product"
    },
    {
        "id": "sora_product_3",
        "name": "Tech Gadget Explainer",
        "model": "sora-2",
        "prompt": "Futuristic tech gadget on a clean, minimalist background, animated UI elements, product features highlighted, professional explainer video style, 4K, innovative technology, sleek design, cinematic presentation",
        "duration": 9,
        "description": "Innovative tech gadget explainer",
        "category": "Product"
    },
    {
        "id": "sora_product_4",
        "name": "Luxury Jewelry Close-up",
        "model": "sora-2",
        "prompt": "Extreme close-up of a sparkling diamond necklace, intricate craftsmanship, elegant studio lighting, slow rotation, luxury commercial style, 4K, high-end jewelry, professional cinematography, exquisite detail",
        "duration": 7,
        "description": "Exquisite luxury jewelry close-up",
        "category": "Product"
    },
    {
        "id": "sora_product_5",
        "name": "Sustainable Brand Story",
        "model": "sora-2",
        "prompt": "Video showcasing a sustainable product, nature-inspired visuals, eco-friendly materials, positive impact story, authentic feel, cinematic documentary style, 4K, ethical branding, professional videography",
        "duration": 8,
        "description": "Inspiring sustainable brand story",
        "category": "Product"
    },
    {
        "id": "sora_product_6",
        "name": "Food Product Packaging",
        "model": "sora-2",
        "prompt": "Close-up of appealing food product packaging, ingredients highlighted, satisfying unboxing or pouring action, clean studio lighting, commercial style, 4K, food marketing, professional videography",
        "duration": 7,
        "description": "Attractive food product packaging",
        "category": "Product"
    },
    
    # --- Lifestyle & Abstract (10 templates) ---
    {
        "id": "runway_lifestyle_1",
        "name": "Morning Coffee Ritual",
        "model": "runway/text-to-video",
        "prompt": "Gentle morning light, steaming cup of coffee on a wooden table, cozy atmosphere, soft focus, slow camera movement, cinematic lifestyle, 4K, peaceful start to the day, professional videography",
        "duration": 8,
        "description": "Relaxing morning coffee scene",
        "category": "Lifestyle"
    },
    {
        "id": "runway_lifestyle_2",
        "name": "Creative Workspace",
        "model": "runway/text-to-video",
        "prompt": "A well-lit, organized creative workspace with a laptop, art supplies, plants, and natural light. Camera pans slowly across the desk. Cinematic lifestyle, 4K, inspiring environment, professional videography",
        "duration": 8,
        "description": "Inspiring creative workspace",
        "category": "Lifestyle"
    },
    {
        "id": "runway_lifestyle_3",
        "name": "Yoga and Wellness",
        "model": "runway/text-to-video",
        "prompt": "Serene yoga session in a calm setting, soft lighting, mindful movements, peaceful atmosphere, cinematic wellness, 4K, healthy lifestyle, professional videography",
        "duration": 8,
        "description": "Peaceful yoga and wellness scene",
        "category": "Lifestyle"
    },
    {
        "id": "sora_lifestyle_1",
        "name": "Travel Exploration Montage",
        "model": "sora-2",
        "prompt": "Dynamic montage of diverse travel experiences: bustling markets, ancient ruins, scenic landscapes, vibrant street life. Energetic music, fast cuts, cinematic travelogue style, 4K, adventure, professional videography",
        "duration": 10,
        "description": "Exciting travel exploration montage",
        "category": "Lifestyle"
    },
    {
        "id": "sora_lifestyle_2",
        "name": "Cozy Bookstore Ambiance",
        "model": "sora-2",
        "prompt": "Warm, inviting bookstore interior, shelves filled with books, soft lamp lighting, people browsing, peaceful atmosphere, cinematic ambiance, 4K, cozy lifestyle, professional videography",
        "duration": 9,
        "description": "Cozy bookstore atmosphere",
        "category": "Lifestyle"
    },
    {
        "id": "sora_lifestyle_3",
        "name": "Outdoor Adventure",
        "model": "sora-2",
        "prompt": "Person hiking on a scenic mountain trail, breathtaking views, sense of freedom and exploration, natural lighting, cinematic adventure style, 4K, active lifestyle, professional videography",
        "duration": 8,
        "description": "Breathtaking outdoor adventure",
        "category": "Lifestyle"
    },
    {
        "id": "sora_lifestyle_4",
        "name": "Urban Exploration Night",
        "model": "sora-2",
        "prompt": "Nighttime urban exploration, neon lights, street art, diverse city scenes, sense of discovery, cinematic style, 4K, modern lifestyle, professional videography",
        "duration": 9,
        "description": "Exciting urban night exploration",
        "category": "Lifestyle"
    },
    {
        "id": "sora_lifestyle_5",
        "name": "Family Gathering",
        "model": "sora-2",
        "prompt": "Warm and joyful family gathering, people laughing, sharing meals, creating memories. Soft natural lighting, authentic emotions, cinematic documentary style, 4K, heartwarming moments, professional videography",
        "duration": 9,
        "description": "Heartwarming family gathering",
        "category": "Lifestyle"
    },
    {
        "id": "sora_abstract_1",
        "name": "Fluid Dynamics",
        "model": "sora-2",
        "prompt": "Mesmerizing abstract visuals of colorful liquids mixing and swirling, fluid dynamics, hypnotic patterns, soft lighting, cinematic art, 4K, mesmerizing motion, professional visual effects",
        "duration": 7,
        "description": "Hypnotic abstract fluid dynamics",
        "category": "Abstract"
    },
    {
        "id": "sora_abstract_2",
        "name": "Geometric Patterns Evolving",
        "model": "sora-2",
        "prompt": "Evolving geometric patterns, intricate fractal designs, vibrant color transitions, abstract digital art, cinematic motion graphics, 4K, mesmerizing visuals, professional design",
        "duration": 7,
        "description": "Mesmerizing evolving geometric patterns",
        "category": "Abstract"
    },
    
    # --- Animation & Cartoons (5 templates) ---
    {
        "id": "sora_animation_1",
        "name": "Whimsical Fairy Tale",
        "model": "sora-2",
        "prompt": "A whimsical fairy tale scene with cute animated characters, magical elements, vibrant colors, charming environment, animated storybook style, 4K, enchanting atmosphere, professional animation",
        "duration": 8,
        "description": "Enchanting whimsical fairy tale",
        "category": "Animation"
    },
    {
        "id": "sora_animation_2",
        "name": "Sci-Fi Cartoon Adventure",
        "model": "sora-2",
        "prompt": "A fun sci-fi cartoon adventure with futuristic robots, alien planets, and exciting action. Bold colors, dynamic animation, comic book style, 4K, high energy, professional animation",
        "duration": 8,
        "description": "Exciting sci-fi cartoon adventure",
        "category": "Animation"
    },
    {
        "id": "sora_animation_3",
        "name": "Character Animation Test",
        "model": "sora-2",
        "prompt": "A detailed animation test of a character performing various actions: walking, jumping, emoting. Focus on fluidity and expressiveness. Professional animation quality, 4K, character performance, detailed rigging",
        "duration": 9,
        "description": "High-quality character animation test",
        "category": "Animation"
    },
    {
        "id": "sora_animation_4",
        "name": "2D Animation Loop",
        "model": "sora-2",
        "prompt": "Seamless 2D animation loop, e.g., a character waving, a subtle environmental effect. Clean line art, vibrant colors, smooth looping, professional animation, 4K, short animation clip",
        "duration": 6,
        "description": "Smooth 2D animation loop",
        "category": "Animation"
    },
    {
        "id": "sora_animation_5",
        "name": "Stop Motion Style",
        "model": "sora-2",
        "prompt": "Video emulating stop-motion animation style, with textured characters and environments, subtle jerky movements, charming and handcrafted feel. Professional cinematography, 4K, unique artistic style",
        "duration": 7,
        "description": "Charming stop-motion style animation",
        "category": "Animation"
    },
    
    # --- Food & Drink (5 templates) ---
    {
        "id": "runway_food_1",
        "name": "Gourmet Cooking Montage",
        "model": "runway/text-to-video",
        "prompt": "A fast-paced gourmet cooking montage showing ingredients being expertly prepared and cooked, steam rising, vibrant food colors, professional kitchen setting, appetizing presentation, cinematic food videography, 4K",
        "duration": 8,
        "description": "High-quality gourmet cooking montage",
        "category": "Food"
    },
    {
        "id": "runway_food_2",
        "name": "Dessert Decoration",
        "model": "runway/text-to-video",
        "prompt": "Close-up of intricate dessert decoration, frosting being piped, fruits being placed, culinary art, soft studio lighting, appetizing visuals, cinematic food videography, 4K, bakery style",
        "duration": 8,
        "description": "Artistic dessert decoration",
        "category": "Food"
    },
    {
        "id": "sora_food_1",
        "name": "Street Food Experience",
        "model": "sora-2",
        "prompt": "Vibrant street food market scene, vendors preparing delicious snacks, diverse culinary offerings, lively atmosphere, cinematic documentary style, 4K, authentic food culture, professional videography",
        "duration": 9,
        "description": "Authentic street food experience",
        "category": "Food"
    },
    {
        "id": "sora_food_2",
        "name": "Farm to Table",
        "model": "sora-2",
        "prompt": "Visual journey from farm fresh ingredients to a beautifully plated meal. Organic produce, rustic kitchen, culinary preparation, cinematic storytelling, 4K, farm-to-table concept, professional videography",
        "duration": 8,
        "description": "Farm to table culinary journey",
        "category": "Food"
    },
    {
        "id": "sora_food_3",
        "name": "Cocktail Creation",
        "model": "sora-2",
        "prompt": "Artistic creation of a sophisticated cocktail, ingredients being mixed and garnished, ice clinking, vibrant colors, elegant bar setting, cinematic drink advertisement style, 4K, mixology, professional videography",
        "duration": 7,
        "description": "Artistic cocktail creation",
        "category": "Food"
    },
]


# --- Image Generation Templates ---

IMAGE_TEMPLATES = [
    {
        "id": "img_1",
        "name": "Product Photography",
        "model": "qwen/image-edit",
        "prompt": "A professional product photo of a luxury watch on a white background with studio lighting, high resolution, sharp details.",
        "description": "Perfect for e-commerce and product marketing.",
        "category": "Product"
    },
    {
        "id": "img_2",
        "name": "Landscape Art",
        "model": "qwen/image-edit",
        "prompt": "A beautiful landscape painting of mountains and lakes at sunset, oil painting style, vibrant colors, artistic composition.",
        "description": "Great for art and design projects.",
        "category": "Art"
    },
    {
        "id": "img_3",
        "name": "Portrait Photography",
        "model": "qwen/image-edit",
        "prompt": "A professional portrait photograph of a person with studio lighting, soft background, high quality, professional photography.",
        "description": "Ideal for headshots and professional profiles.",
        "category": "Portrait"
    },
    {
        "id": "img_4",
        "name": "Food Photography",
        "model": "qwen/image-edit",
        "prompt": "Gourmet dish plated beautifully on white ceramic, natural lighting, shallow depth of field, professional food photography, appetizing presentation.",
        "description": "Mouth-watering food imagery for restaurants.",
        "category": "Food"
    },
    {
        "id": "img_5",
        "name": "Architecture Modern",
        "model": "qwen/image-edit",
        "prompt": "Modern minimalist architecture with clean lines, glass and concrete, blue sky, professional architectural photography, sharp details.",
        "description": "Stunning architectural visualization.",
        "category": "Architecture"
    },
    {
        "id": "img_6",
        "name": "Abstract Digital Art",
        "model": "qwen/image-edit",
        "prompt": "Abstract digital art with flowing shapes, vibrant gradients, modern design, geometric patterns, contemporary style.",
        "description": "Eye-catching abstract designs.",
        "category": "Art"
    },
    {
        "id": "img_7",
        "name": "Nature Macro",
        "model": "qwen/image-edit",
        "prompt": "Extreme macro photography of a dewdrop on a leaf, crystal clear, bokeh background, natural lighting, stunning detail.",
        "description": "Intricate nature close-ups.",
        "category": "Nature"
    },
    {
        "id": "img_8",
        "name": "Fashion Editorial",
        "model": "qwen/image-edit",
        "prompt": "High fashion editorial photograph, dramatic lighting, elegant pose, designer clothing, professional styling, magazine quality.",
        "description": "High-end fashion imagery.",
        "category": "Fashion"
    },
    {
        "id": "img_9",
        "name": "Tech Product",
        "model": "qwen/image-edit",
        "prompt": "Sleek tech gadget on gradient background, modern design, LED accents, futuristic aesthetic, product photography.",
        "description": "Modern tech product shots.",
        "category": "Product"
    },
    {
        "id": "img_10",
        "name": "Workspace Flat Lay",
        "model": "qwen/image-edit",
        "prompt": "Flat lay of organized workspace with laptop, coffee, notebook, plants, minimal aesthetic, top-down view, natural light.",
        "description": "Popular social media content style.",
        "category": "Lifestyle"
    },
    # --- Nature & Landscapes ---
    {
        "id": "img_nature_1",
        "name": "Mountain Vista",
        "model": "qwen/image-edit",
        "prompt": "Panoramic view of a majestic mountain range at sunrise, golden hour light, dramatic clouds, hyper-realistic.",
        "description": "Stunning natural landscape.",
        "category": "Nature"
    },
    {
        "id": "img_nature_2",
        "name": "Tropical Beach",
        "model": "qwen/image-edit",
        "prompt": "Idyllic tropical beach scene, turquoise water, white sand, palm trees, clear blue sky, photorealistic.",
        "description": "Beautiful beach scenery.",
        "category": "Nature"
    },
    {
        "id": "img_nature_3",
        "name": "Enchanted Forest",
        "model": "qwen/image-edit",
        "prompt": "Magical forest path with sunbeams filtering through ancient trees, mossy ground, ethereal atmosphere, fantasy art.",
        "description": "Mystical forest imagery.",
        "category": "Nature"
    },
    {
        "id": "img_nature_4",
        "name": "Desert Dunes",
        "model": "qwen/image-edit",
        "prompt": "Vast desert dunes under a clear sky, soft sand textures, warm lighting, abstract patterns, photorealistic.",
        "description": "Arid landscape.",
        "category": "Nature"
    },
    {
        "id": "img_nature_5",
        "name": "Aurora Borealis",
        "model": "qwen/image-edit",
        "prompt": "Vibrant aurora borealis dancing in a starry night sky over a snowy landscape, magical, ethereal.",
        "description": "Celestial phenomenon.",
        "category": "Nature"
    },
    # --- Urban & Cityscapes ---
    {
        "id": "img_urban_1",
        "name": "Cyberpunk Cityscape",
        "model": "qwen/image-edit",
        "prompt": "Futuristic cyberpunk city at night, neon lights, flying vehicles, rain-slicked streets, dramatic, high detail.",
        "description": "Dystopian urban future.",
        "category": "Urban"
    },
    {
        "id": "img_urban_2",
        "name": "Parisian Cafe",
        "model": "qwen/image-edit",
        "prompt": "Charming Parisian street cafe scene, cobblestone street, Eiffel Tower in background, warm lighting, romantic atmosphere, watercolor style.",
        "description": "Romantic city ambiance.",
        "category": "Urban"
    },
    {
        "id": "img_urban_3",
        "name": "Modern Skyscraper",
        "model": "qwen/image-edit",
        "prompt": "Sleek modern skyscraper with glass facade reflecting blue sky, architectural photography, clean lines, minimalist.",
        "description": "Contemporary architecture.",
        "category": "Urban"
    },
    {
        "id": "img_urban_4",
        "name": "Busy Market Street",
        "model": "qwen/image-edit",
        "prompt": "Bustling street market with diverse stalls, colorful produce, people interacting, vibrant energy, photorealistic.",
        "description": "Lively urban market.",
        "category": "Urban"
    },
    {
        "id": "img_urban_5",
        "name": "Vintage Cityscape",
        "model": "qwen/image-edit",
        "prompt": "A vintage cityscape with classic cars and old buildings, sepia tones, nostalgic atmosphere, retro photography.",
        "description": "Nostalgic city view.",
        "category": "Urban"
    },
    # --- Sci-Fi & Fantasy ---
    {
        "id": "img_scifi_1",
        "name": "Alien Planet Surface",
        "model": "qwen/image-edit",
        "prompt": "Exotic alien planet surface with strange flora and fauna, twin moons in sky, sci-fi concept art.",
        "description": "Otherworldly landscape.",
        "category": "Sci-Fi"
    },
    {
        "id": "img_scifi_2",
        "name": "Spaceship Interior",
        "model": "qwen/image-edit",
        "prompt": "Futuristic spaceship bridge interior with holographic displays and advanced control panels, sci-fi, cinematic.",
        "description": "High-tech interior.",
        "category": "Sci-Fi"
    },
    {
        "id": "img_scifi_3",
        "name": "Dragon Guardian",
        "model": "qwen/image-edit",
        "prompt": "A majestic dragon guarding a treasure hoard in a dark cave, fantasy art, epic scale, dramatic lighting.",
        "description": "Mythical creature.",
        "category": "Fantasy"
    },
    {
        "id": "img_scifi_4",
        "name": "Magic Portal",
        "model": "qwen/image-edit",
        "prompt": "Glowing magical portal swirling with energy, emanating light, fantasy concept art, mysterious.",
        "description": "Enigmatic gateway.",
        "category": "Fantasy"
    },
    {
        "id": "img_scifi_5",
        "name": "Robot Companion",
        "model": "qwen/image-edit",
        "prompt": "Friendly robot companion with sleek design, standing in a modern setting, sci-fi, photorealistic.",
        "description": "Futuristic AI.",
        "category": "Sci-Fi"
    },
    # --- Animation & Cartoons ---
    {
        "id": "img_anim_1",
        "name": "Cute Cartoon Character",
        "model": "qwen/image-edit",
        "prompt": "A cute and expressive cartoon character, whimsical design, vibrant colors, 2D animation style.",
        "description": "Charming animated character.",
        "category": "Animation"
    },
    {
        "id": "img_anim_2",
        "name": "Fantasy Creature Cartoon",
        "model": "qwen/image-edit",
        "prompt": "A stylized fantasy creature in a cartoon style, playful and colorful, suitable for children's stories.",
        "description": "Playful fantasy creature.",
        "category": "Animation"
    },
    {
        "id": "img_anim_3",
        "name": "Pixel Art Landscape",
        "model": "qwen/image-edit",
        "prompt": "A retro pixel art landscape, 8-bit style, vibrant colors, charming game-like environment.",
        "description": "Retro gaming aesthetic.",
        "category": "Animation"
    },
    # --- Food & Drink ---
    {
        "id": "img_food_1",
        "name": "Artisan Bread",
        "model": "qwen/image-edit",
        "prompt": "Artisan sourdough bread loaf with a golden crust, on a rustic wooden board, studio lighting, mouth-watering.",
        "description": "Delicious baked goods.",
        "category": "Food"
    },
    {
        "id": "img_food_2",
        "name": "Exotic Fruit Platter",
        "model": "qwen/image-edit",
        "prompt": "Vibrant platter of exotic fruits, fresh and colorful, tropical theme, high resolution, appetizing.",
        "description": "Healthy and colorful food.",
        "category": "Food"
    },
    {
        "id": "img_food_3",
        "name": "Gourmet Coffee",
        "model": "qwen/image-edit",
        "prompt": "Close-up of a steaming gourmet coffee cup with latte art, cozy atmosphere, bokeh background, professional food photography.",
        "description": "Inviting coffee shot.",
        "category": "Food"
    },
    # --- Fashion & Beauty ---
    {
        "id": "img_fashion_1",
        "name": "Haute Couture Dress",
        "model": "qwen/image-edit",
        "prompt": "Elegant haute couture dress on a mannequin, luxurious fabric, intricate details, dramatic studio lighting, fashion photography.",
        "description": "High fashion design.",
        "category": "Fashion"
    },
    {
        "id": "img_fashion_2",
        "name": "Luxury Perfume Bottle",
        "model": "qwen/image-edit",
        "prompt": "Luxury perfume bottle with elegant design, soft lighting, reflections, premium product shot.",
        "description": "Elegant fragrance.",
        "category": "Fashion"
    },
    {
        "id": "img_fashion_3",
        "name": "Glamorous Makeup",
        "model": "qwen/image-edit",
        "prompt": "Close-up of glamorous eye makeup with bold colors and glitter, high detail, beauty photography.",
        "description": "Stunning makeup artistry.",
        "category": "Fashion"
    },
    # --- Business & Technology ---
    {
        "id": "img_biz_1",
        "name": "Modern Office Interior",
        "model": "qwen/image-edit",
        "prompt": "Modern, minimalist office interior with sleek furniture, natural light, plants, and a clean aesthetic.",
        "description": "Professional workspace.",
        "category": "Business"
    },
    {
        "id": "img_biz_2",
        "name": "Data Visualization",
        "model": "qwen/image-edit",
        "prompt": "Abstract digital representation of data visualization, glowing nodes and connections, futuristic, tech-themed.",
        "description": "Innovative data graphics.",
        "category": "Technology"
    },
    {
        "id": "img_biz_3",
        "name": "Abstract Network",
        "model": "qwen/image-edit",
        "prompt": "Abstract glowing network of interconnected lines and nodes, representing technology and connectivity, futuristic.",
        "description": "Digital connectivity.",
        "category": "Technology"
    },
    # --- Abstract & Conceptual ---
    {
        "id": "img_abstract_1",
        "name": "Geometric Abstraction",
        "model": "qwen/image-edit",
        "prompt": "Abstract composition of geometric shapes in vibrant colors, modern design, minimalist.",
        "description": "Modern geometric art.",
        "category": "Abstract"
    },
    {
        "id": "img_abstract_2",
        "name": "Dreamlike Surreal",
        "model": "qwen/image-edit",
        "prompt": "Surreal dreamlike scene with floating objects and unusual combinations, artistic, conceptual.",
        "description": "Imaginative conceptual art.",
        "category": "Abstract"
    },
    {
        "id": "img_abstract_3",
        "name": "Splashing Paint",
        "model": "qwen/image-edit",
        "prompt": "Dynamic explosion of colorful paint splashing, abstract expressionism, high speed photography.",
        "description": "Vibrant paint dynamics.",
        "category": "Abstract"
    },
    # --- People & Lifestyle ---
    {
        "id": "img_people_1",
        "name": "Happy Family Outdoors",
        "model": "qwen/image-edit",
        "prompt": "A happy family enjoying a picnic in a park, natural sunlight, joyful expressions, lifestyle photography.",
        "description": "Heartwarming family moment.",
        "category": "Lifestyle"
    },
    {
        "id": "img_people_2",
        "name": "Person Reading Book",
        "model": "qwen/image-edit",
        "prompt": "Person engrossed in reading a book by a window, cozy interior, soft lighting, peaceful atmosphere.",
        "description": "Quiet relaxing moment.",
        "category": "Lifestyle"
    },
    {
        "id": "img_people_3",
        "name": "Couple Dancing",
        "model": "qwen/image-edit",
        "prompt": "Couple dancing romantically in a dimly lit room, elegant motion, soft focus, emotional.",
        "description": "Romantic couple scene.",
        "category": "Lifestyle"
    },
    # --- Travel & Adventure ---
    {
        "id": "img_travel_1",
        "name": "Ancient Ruins",
        "model": "qwen/image-edit",
        "prompt": "Majestic ancient ruins in a scenic landscape, historical atmosphere, detailed stonework, golden hour lighting.",
        "description": "Historical exploration.",
        "category": "Travel"
    },
    {
        "id": "img_travel_2",
        "name": "City at Night",
        "model": "qwen/image-edit",
        "prompt": "Vibrant cityscape at night, illuminated skyscrapers, car light trails, energetic atmosphere, photorealistic.",
        "description": "Dynamic urban night view.",
        "category": "Travel"
    },
    {
        "id": "img_travel_3",
        "name": "Mountain Peak",
        "model": "qwen/image-edit",
        "prompt": "Breathtaking view from a mountain peak, vast sky, clouds below, sense of achievement, epic landscape.",
        "description": "Adventurous high altitude.",
        "category": "Travel"
    },
]

# --- Prompt Collection System ---

PROMPT_CATEGORIES = {
    "cinematic": {
        "name": "Cinematic & Film",
        "description": "Professional film and video production styles",
        "prompts": [
            {
                "title": "Epic Establishing Shot",
                "prompt": "Wide-angle cinematic establishing shot, dramatic lighting, golden hour, professional color grading, 4K quality, film grain, anamorphic lens flare, epic scale",
                "tags": ["wide-angle", "dramatic", "establishing", "epic"]
            },
            {
                "title": "Intimate Close-up",
                "prompt": "Extreme close-up shot, shallow depth of field, cinematic bokeh, emotional lighting, film quality, professional cinematography, 85mm lens, soft focus background",
                "tags": ["close-up", "emotional", "bokeh", "intimate"]
            },
            {
                "title": "Tracking Shot Movement",
                "prompt": "Smooth tracking shot following subject, steady cam movement, cinematic framing, professional lighting, dynamic composition, fluid camera work, professional cinematography",
                "tags": ["tracking", "movement", "dynamic", "smooth"]
            },
            {
                "title": "Drone Aerial Sweep",
                "prompt": "Aerial drone footage, sweeping camera movement, bird's eye view, cinematic scale, professional color grading, establishing shot, epic landscape, 4K quality",
                "tags": ["aerial", "drone", "sweeping", "epic"]
            },
            {
                "title": "Slow Motion Drama",
                "prompt": "Slow motion cinematic shot, 120fps, dramatic timing, professional lighting, emotional impact, film quality, time manipulation, artistic cinematography",
                "tags": ["slow-motion", "dramatic", "emotional", "artistic"]
            },
            {
                "title": "Dutch Angle Tension",
                "prompt": "Dutch angle shot, tilted camera, psychological tension, cinematic technique, dramatic framing, professional cinematography, unsettling composition, artistic choice",
                "tags": ["dutch-angle", "tension", "dramatic", "artistic"]
            },
            {
                "title": "POV First Person",
                "prompt": "First-person POV shot, immersive perspective, subjective camera, engaging viewpoint, cinematic storytelling, realistic movement, professional technique",
                "tags": ["pov", "first-person", "immersive", "subjective"]
            },
            {
                "title": "Crane Shot Rising",
                "prompt": "Crane shot rising up, revealing landscape, cinematic movement, professional cinematography, dramatic reveal, smooth motion, epic scale, 4K quality",
                "tags": ["crane", "rising", "reveal", "epic"]
            },
            {
                "title": "Dolly Zoom Effect",
                "prompt": "Dolly zoom vertigo effect, Hitchcock technique, dramatic perspective shift, cinematic impact, professional execution, psychological effect, artistic cinematography",
                "tags": ["dolly-zoom", "vertigo", "dramatic", "hitchcock"]
            },
            {
                "title": "Steadicam Follow",
                "prompt": "Steadicam following shot, smooth movement, professional tracking, cinematic flow, dynamic composition, fluid camera work, immersive perspective",
                "tags": ["steadicam", "following", "smooth", "dynamic"]
            },
        ]
    },
    "lighting": {
        "name": "Lighting Styles",
        "description": "Professional lighting techniques and moods",
        "prompts": [
            {
                "title": "Golden Hour Magic",
                "prompt": "Golden hour lighting, warm tones, soft shadows, magical atmosphere, natural sunlight, professional photography, 30 minutes before sunset, glowing quality",
                "tags": ["golden-hour", "warm", "natural", "magical"]
            },
            {
                "title": "Neon Noir Atmosphere",
                "prompt": "Neon lighting, cyberpunk aesthetic, dramatic shadows, vibrant colors, noir atmosphere, cinematic mood, electric glow, urban night, high contrast",
                "tags": ["neon", "cyberpunk", "noir", "dramatic"]
            },
            {
                "title": "Studio Three-Point",
                "prompt": "Professional studio lighting, three-point setup, key light, fill light, rim light, soft shadows, clean background, commercial quality, balanced exposure",
                "tags": ["studio", "professional", "clean", "balanced"]
            },
            {
                "title": "Moody Dramatic Shadows",
                "prompt": "Dramatic moody lighting, high contrast, deep shadows, atmospheric, cinematic noir, professional grade, chiaroscuro technique, emotional impact",
                "tags": ["moody", "dramatic", "contrast", "shadows"]
            },
            {
                "title": "Soft Natural Window",
                "prompt": "Soft natural window light, diffused sunlight, gentle shadows, intimate atmosphere, professional portrait lighting, warm tones, organic feel",
                "tags": ["natural", "soft", "window", "intimate"]
            },
            {
                "title": "Blue Hour Twilight",
                "prompt": "Blue hour twilight lighting, cool tones, magical atmosphere, civil twilight, professional photography, ethereal quality, soft ambient light",
                "tags": ["blue-hour", "twilight", "cool", "ethereal"]
            },
            {
                "title": "Rembrandt Portrait",
                "prompt": "Rembrandt lighting technique, triangle of light on cheek, dramatic portrait, classical style, professional photography, artistic shadows, timeless quality",
                "tags": ["rembrandt", "portrait", "classical", "dramatic"]
            },
            {
                "title": "Backlit Silhouette",
                "prompt": "Backlit silhouette, rim lighting, dramatic contrast, subject in shadow, professional cinematography, artistic composition, powerful visual",
                "tags": ["backlit", "silhouette", "dramatic", "artistic"]
            },
            {
                "title": "Volumetric God Rays",
                "prompt": "Volumetric lighting, god rays, light beams through atmosphere, cinematic quality, dramatic effect, professional cinematography, ethereal mood",
                "tags": ["volumetric", "god-rays", "dramatic", "ethereal"]
            },
            {
                "title": "Practical Light Sources",
                "prompt": "Practical lighting from visible sources, realistic atmosphere, cinematic naturalism, professional technique, motivated lighting, authentic feel",
                "tags": ["practical", "realistic", "natural", "authentic"]
            },
        ]
    },
    "style": {
        "name": "Visual Styles",
        "description": "Artistic and visual style modifiers",
        "prompts": [
            {
                "title": "Photorealistic Hyperdetail",
                "prompt": "Hyper-realistic, photorealistic quality, ultra-detailed, sharp focus, professional photography, 8K resolution, intricate textures, lifelike appearance",
                "tags": ["realistic", "detailed", "sharp", "ultra-hd"]
            },
            {
                "title": "3D Animated Pixar",
                "prompt": "3D animated style, Pixar quality, vibrant colors, smooth rendering, professional animation, detailed textures, stylized realism, family-friendly",
                "tags": ["3d", "animated", "pixar", "stylized"]
            },
            {
                "title": "Oil Painting Masterpiece",
                "prompt": "Oil painting style, artistic brushstrokes, rich colors, classical art, museum quality, fine art, impasto technique, textured canvas",
                "tags": ["painting", "artistic", "classical", "fine-art"]
            },
            {
                "title": "Minimalist Modern Design",
                "prompt": "Minimalist design, clean lines, modern aesthetic, simple composition, professional design, elegant, uncluttered, negative space",
                "tags": ["minimalist", "modern", "clean", "elegant"]
            },
            {
                "title": "Watercolor Wash",
                "prompt": "Watercolor painting style, soft edges, translucent colors, painterly texture, artistic expression, delicate hues",
                "tags": ["watercolor", "painterly", "artistic", "delicate"]
            },
            {
                "title": "Comic Book Art",
                "prompt": "Comic book art style, bold outlines, vibrant colors, dynamic poses, graphic novel aesthetic, action-packed",
                "tags": ["comic", "graphic-novel", "bold", "action"]
            },
            {
                "title": "Retro Vintage Film",
                "prompt": "Retro vintage film look, faded colors, film grain, soft focus, nostalgic aesthetic, 1970s style, analog photography",
                "tags": ["retro", "vintage", "film", "nostalgic"]
            },
            {
                "title": "Claymation Stop Motion",
                "prompt": "Claymation stop-motion style, textured characters, slightly jerky movements, handcrafted feel, charming, quirky",
                "tags": ["claymation", "stop-motion", "handcrafted", "quirky"]
            },
            {
                "title": "Anime Vibrant",
                "prompt": "Vibrant anime art style, sharp lines, expressive characters, dynamic action, Japanese animation influence",
                "tags": ["anime", "japanese", "vibrant", "expressive"]
            },
            {
                "title": "Line Art Minimal",
                "prompt": "Minimalist line art, simple black and white, clean outlines, elegant design, conceptual illustration",
                "tags": ["line-art", "minimalist", "clean", "conceptual"]
            },
        ]
    },
    "atmosphere": {
        "name": "Atmosphere & Mood",
        "description": "Emotional and atmospheric qualities",
        "prompts": [
            {
                "title": "Peaceful Serene Calm",
                "prompt": "Peaceful atmosphere, serene mood, calm colors, gentle lighting, tranquil setting, meditative quality, relaxing, quiet",
                "tags": ["peaceful", "serene", "calm", "relaxing"]
            },
            {
                "title": "Epic Dramatic Powerful",
                "prompt": "Epic scale, dramatic atmosphere, powerful composition, intense mood, cinematic grandeur, awe-inspiring, heroic, monumental",
                "tags": ["epic", "dramatic", "powerful", "awe-inspiring"]
            },
            {
                "title": "Mysterious Dark Shadowy",
                "prompt": "Mysterious atmosphere, dark mood, shadowy, enigmatic, suspenseful, cinematic tension, foreboding, eerie",
                "tags": ["mysterious", "dark", "shadowy", "suspenseful"]
            },
            {
                "title": "Energetic Vibrant Lively",
                "prompt": "Energetic atmosphere, vibrant colors, dynamic composition, lively mood, exciting, high energy, pulsating, spirited",
                "tags": ["energetic", "vibrant", "dynamic", "lively"]
            },
            {
                "title": "Romantic Dreamlike",
                "prompt": "Romantic atmosphere, dreamlike quality, soft focus, ethereal lighting, gentle mood, enchanting, whimsical",
                "tags": ["romantic", "dreamlike", "ethereal", "enchanting"]
            },
            {
                "title": "Gloomy Melancholy",
                "prompt": "Gloomy atmosphere, melancholy mood, muted colors, overcast lighting, somber, introspective",
                "tags": ["gloomy", "melancholy", "muted", "somber"]
            },
            {
                "title": "Whimsical Playful",
                "prompt": "Whimsical atmosphere, playful mood, lighthearted, fun, cheerful, imaginative, fantasy-like",
                "tags": ["whimsical", "playful", "lighthearted", "fun"]
            },
            {
                "title": "Tense Suspenseful",
                "prompt": "Tense atmosphere, suspenseful mood, anticipation, build-up, dramatic tension, thrilling, ominous",
                "tags": ["tense", "suspenseful", "anticipation", "thrilling"]
            },
            {
                "title": "Nostalgic Retro",
                "prompt": "Nostalgic atmosphere, retro feel, vintage aesthetic, warmth, sentimental, reminiscent",
                "tags": ["nostalgic", "retro", "vintage", "sentimental"]
            },
            {
                "title": "Ethereal Magical",
                "prompt": "Ethereal atmosphere, magical quality, otherworldly, mystical, enchanting, luminous, divine",
                "tags": ["ethereal", "magical", "otherworldly", "enchanting"]
            },
        ]
    },
    "camera": {
        "name": "Camera Techniques",
        "description": "Professional camera movements and angles",
        "prompts": [
            {
                "title": "Slow Motion Smooth",
                "prompt": "Slow motion footage, high frame rate, smooth movement, dramatic timing, professional cinematography, artistic choice, 120fps",
                "tags": ["slow-motion", "smooth", "dramatic", "artistic"]
            },
            {
                "title": "Time Lapse Dynamic",
                "prompt": "Time-lapse photography, accelerated time, smooth transitions, dynamic change, professional technique, cityscapes, nature",
                "tags": ["time-lapse", "accelerated", "dynamic", "transition"]
            },
            {
                "title": "Dutch Angle Tilted",
                "prompt": "Dutch angle shot, tilted camera, dynamic composition, cinematic technique, dramatic framing, artistic choice, unsettling perspective",
                "tags": ["dutch-angle", "tilted", "dynamic", "artistic"]
            },
            {
                "title": "POV First Person Immersive",
                "prompt": "First-person POV, immersive perspective, subjective camera, engaging viewpoint, cinematic storytelling, realistic movement, direct experience",
                "tags": ["pov", "first-person", "immersive", "subjective"]
            },
            {
                "title": "Crane Shot Reveal",
                "prompt": "Crane shot rising up, revealing landscape or subject, cinematic movement, dramatic reveal, smooth motion, epic scale, expansive view",
                "tags": ["crane", "reveal", "cinematic", "epic"]
            },
            {
                "title": "Dolly Zoom Vertigo",
                "prompt": "Dolly zoom vertigo effect, Hitchcock technique, dramatic perspective shift, cinematic impact, psychological effect, unsettling",
                "tags": ["dolly-zoom", "vertigo", "dramatic", "hitchcock"]
            },
            {
                "title": "Steadicam Smooth Follow",
                "prompt": "Steadicam following shot, smooth movement, professional tracking, cinematic flow, dynamic composition, fluid camera work, immersive",
                "tags": ["steadicam", "smooth", "following", "dynamic"]
            },
            {
                "title": "Handheld Shaky",
                "prompt": "Handheld camera feel, shaky movement, raw and immediate, documentary style, intense action, subjective perspective",
                "tags": ["handheld", "shaky", "raw", "documentary"]
            },
            {
                "title": "Extreme Wide Angle",
                "prompt": "Extreme wide-angle lens, expansive view, distorted perspective at edges, dramatic landscape, immersive",
                "tags": ["wide-angle", "expansive", "dramatic", "immersive"]
            },
            {
                "title": "Macro Extreme Close-up",
                "prompt": "Macro lens, extreme close-up, focus on minute details, textures, shallow depth of field, intimate perspective",
                "tags": ["macro", "close-up", "detail", "intimate"]
            },
        ]
    },
    "genre": {
        "name": "Genre Specific",
        "description": "Genre-specific visual styles",
        "prompts": [
            {
                "title": "Sci-Fi Futuristic Tech",
                "prompt": "Futuristic sci-fi aesthetic, advanced technology, neon accents, cyberpunk elements, high-tech atmosphere, alien landscapes, spacecraft",
                "tags": ["sci-fi", "futuristic", "tech", "cyberpunk"]
            },
            {
                "title": "Fantasy Magical Enchanted",
                "prompt": "Fantasy atmosphere, magical elements, ethereal lighting, mystical mood, enchanted setting, dragons, wizards, mythical creatures",
                "tags": ["fantasy", "magical", "mystical", "enchanted"]
            },
            {
                "title": "Horror Suspense Eerie",
                "prompt": "Horror atmosphere, suspenseful mood, dark shadows, eerie lighting, tension building, cinematic fear, haunted, monstrous",
                "tags": ["horror", "suspense", "eerie", "haunted"]
            },
            {
                "title": "Documentary Authentic Realistic",
                "prompt": "Documentary style, authentic feel, natural lighting, realistic portrayal, journalistic approach, real-life subjects",
                "tags": ["documentary", "authentic", "realistic", "journalistic"]
            },
            {
                "title": "Steampunk Retrofuturism",
                "prompt": "Steampunk aesthetic, Victorian era meets futuristic technology, gears, brass, steam power, retrofuturism",
                "tags": ["steampunk", "retrofuturism", "victorian", "gears"]
            },
            {
                "title": "Cyberpunk Dystopian",
                "prompt": "Cyberpunk dystopian setting, gritty urban environments, advanced tech, social decay, neon-drenched streets, noir elements",
                "tags": ["cyberpunk", "dystopian", "gritty", "noir"]
            },
            {
                "title": "Medieval Fantasy Epic",
                "prompt": "Medieval fantasy setting, castles, knights, mythical beasts, epic battles, historical fantasy",
                "tags": ["medieval", "fantasy", "epic", "knights"]
            },
            {
                "title": "Post-Apocalyptic Ruined",
                "prompt": "Post-apocalyptic world, ruined cities, survival themes, desolate landscapes, wasteland",
                "tags": ["post-apocalyptic", "ruined", "wasteland", "survival"]
            },
            {
                "title": "Noir Mystery",
                "prompt": "Film noir style, mystery, dark shadows, femme fatales, detective stories, high contrast lighting",
                "tags": ["noir", "mystery", "detective", "shadows"]
            },
            {
                "title": "Western Frontier",
                "prompt": "Wild West frontier setting, cowboys, saloons, dusty towns, classic western aesthetic",
                "tags": ["western", "cowboy", "frontier", "saloon"]
            },
        ]
    },
    "technical": {
        "name": "Technical Modifiers",
        "description": "Modifiers related to image/video quality and rendering",
        "prompts": [
            {
                "title": "4K Ultra HD",
                "prompt": "4K resolution, Ultra HD, high detail, sharp focus, crisp image, professional quality",
                "tags": ["4k", "uhd", "high-resolution", "detail"]
            },
            {
                "title": "8K Cinematic",
                "prompt": "8K resolution, cinematic quality, extreme detail, photorealistic, professional cinematography",
                "tags": ["8k", "cinematic", "photorealistic", "professional"]
            },
            {
                "title": "Photorealistic Realistic",
                "prompt": "Photorealistic, lifelike, true-to-life, realistic textures, natural lighting, high fidelity",
                "tags": ["photorealistic", "realistic", "lifelike", "high-fidelity"]
            },
            {
                "title": "Shallow Depth of Field",
                "prompt": "Shallow depth of field, blurred background, bokeh effect, focus on subject, cinematic portraiture",
                "tags": ["dof", "bokeh", "focus", "portrait"]
            },
            {
                "title": "Anamorphic Lens Flare",
                "prompt": "Anamorphic lens flare, cinematic aspect ratio, wide screen, stylized light streaks, filmic effect",
                "tags": ["anamorphic", "lens-flare", "cinematic", "filmic"]
            },
            {
                "title": "Film Grain Texture",
                "prompt": "Film grain, analog film look, subtle texture, classic cinema aesthetic, vintage feel",
                "tags": ["film-grain", "analog", "vintage", "texture"]
            },
            {
                "title": "VFX Visual Effects",
                "prompt": "Advanced visual effects (VFX), CGI, special effects, seamless integration, high-quality rendering",
                "tags": ["vfx", "cgi", "special-effects", "rendering"]
            },
            {
                "title": "High Dynamic Range (HDR)",
                "prompt": "High Dynamic Range (HDR), vivid colors, deep contrast, enhanced detail in shadows and highlights, photorealistic",
                "tags": ["hdr", "high-dynamic-range", "vivid", "contrast"]
            },
            {
                "title": "Global Illumination",
                "prompt": "Global illumination rendering, realistic light bounce, soft ambient occlusion, natural lighting simulation",
                "tags": ["global-illumination", "realistic-lighting", "ambient-occlusion"]
            },
            {
                "title": "Physically Based Rendering (PBR)",
                "prompt": "Physically Based Rendering (PBR), realistic material properties, accurate light interaction, high-fidelity surfaces",
                "tags": ["pbr", "physically-based-rendering", "realistic-materials"]
            },
        ]
    },
    "subject": {
        "name": "Subject Matter",
        "description": "Common subjects and themes",
        "prompts": [
            {
                "title": "City Streets Night",
                "prompt": "Bustling city streets at night, neon lights, rain, urban atmosphere, cinematic",
                "tags": ["city", "street", "night", "urban"]
            },
            {
                "title": "Mountain Landscape Sunrise",
                "prompt": "Majestic mountain landscape at sunrise, golden hour, epic vista, nature photography",
                "tags": ["mountain", "landscape", "sunrise", "nature"]
            },
            {
                "title": "Ocean Waves Shore",
                "prompt": "Crashing ocean waves on a sandy shore, dramatic lighting, serene or powerful atmosphere",
                "tags": ["ocean", "waves", "shore", "sea"]
            },
            {
                "title": "Forest Trail Path",
                "prompt": "Tranquil forest trail, sunlight filtering through trees, peaceful atmosphere, nature",
                "tags": ["forest", "trail", "path", "nature"]
            },
            {
                "title": "Abstract Geometric Shapes",
                "prompt": "Abstract geometric shapes, vibrant colors, minimalist design, modern art",
                "tags": ["abstract", "geometric", "shapes", "modern-art"]
            },
            {
                "title": "Futuristic Spaceship",
                "prompt": "Sleek futuristic spaceship in deep space, stars, nebulae, sci-fi",
                "tags": ["spaceship", "futuristic", "sci-fi", "space"]
            },
            {
                "title": "Fantasy Castle Kingdom",
                "prompt": "Magnificent fantasy castle overlooking a kingdom, epic scale, mythical architecture",
                "tags": ["fantasy", "castle", "kingdom", "mythical"]
            },
            {
                "title": "Portrait Person Face",
                "prompt": "Close-up portrait of a person, expressive face, professional lighting, studio quality",
                "tags": ["portrait", "person", "face", "studio"]
            },
            {
                "title": "Product Tech Gadget",
                "prompt": "Sleek tech gadget, modern design, clean background, product photography",
                "tags": ["product", "tech", "gadget", "modern"]
            },
            {
                "title": "Food Cuisine Meal",
                "prompt": "Delicious gourmet food dish, appetizing presentation, high-quality photography",
                "tags": ["food", "cuisine", "meal", "gourmet"]
            },
        ]
    },
    "action": {
        "name": "Action & Movement",
        "description": "Prompts describing movement and dynamic actions",
        "prompts": [
            {
                "title": "Running Fast Motion",
                "prompt": "Person or creature running at high speed, motion blur, dynamic action, sense of urgency",
                "tags": ["running", "fast", "motion", "action"]
            },
            {
                "title": "Flying Soaring",
                "prompt": "Character or object flying through the air, soaring motion, freedom, aerial view",
                "tags": ["flying", "soaring", "aerial", "freedom"]
            },
            {
                "title": "Exploding Burst",
                "prompt": "Object or substance exploding, chaotic burst, energy release, dramatic effect",
                "tags": ["exploding", "burst", "chaos", "energy"]
            },
            {
                "title": "Falling Dropping",
                "prompt": "Object falling or dropping, sense of gravity, motion blur, impact or descent",
                "tags": ["falling", "dropping", "gravity", "descent"]
            },
            {
                "title": "Spinning Rotating",
                "prompt": "Object or character spinning or rotating, dizzying motion, fluid movement, circular path",
                "tags": ["spinning", "rotating", "motion", "fluid"]
            },
            {
                "title": "Jumping Leaping",
                "prompt": "Person or animal jumping or leaping, dynamic pose, action shot, overcoming obstacle",
                "tags": ["jumping", "leaping", "action", "dynamic"]
            },
            {
                "title": "Colliding Impact",
                "prompt": "Two objects or forces colliding, impact, explosion, dramatic collision",
                "tags": ["colliding", "impact", "collision", "explosion"]
            },
            {
                "title": "Flowing Liquid Water",
                "prompt": "Liquid flowing, water movement, graceful curves, dynamic fluid simulation",
                "tags": ["flowing", "liquid", "water", "fluid"]
            },
            {
                "title": "Breathing Expanding",
                "prompt": "Object or entity expanding or breathing, rhythmic motion, organic movement, subtle growth",
                "tags": ["breathing", "expanding", "motion", "organic"]
            },
            {
                "title": "Shaking Vibrating",
                "prompt": "Object or ground shaking or vibrating, tremors, instability, intense motion",
                "tags": ["shaking", "vibrating", "tremor", "instability"]
            },
        ]
    },
    "composition": {
        "name": "Composition & Framing",
        "description": "Elements related to how the scene is framed",
        "prompts": [
            {
                "title": "Symmetrical Balanced",
                "prompt": "Symmetrical composition, balanced elements, harmonious arrangement, centered subject",
                "tags": ["symmetrical", "balanced", "harmonious", "centered"]
            },
            {
                "title": "Asymmetrical Dynamic",
                "prompt": "Asymmetrical composition, dynamic balance, unequal elements, engaging flow",
                "tags": ["asymmetrical", "dynamic", "flow", "unequal"]
            },
            {
                "title": "Rule of Thirds",
                "prompt": "Composition following the rule of thirds, placing subjects off-center for visual interest",
                "tags": ["rule-of-thirds", "composition", "visual-interest", "off-center"]
            },
            {
                "title": "Leading Lines",
                "prompt": "Composition featuring leading lines guiding the viewer's eye through the scene",
                "tags": ["leading-lines", "composition", "guidance", "eye-path"]
            },
            {
                "title": "Framing Device",
                "prompt": "Subject framed by foreground elements, e.g., doorway, window, branches, creating depth",
                "tags": ["framing", "depth", "foreground", "layers"]
            },
            {
                "title": "Negative Space",
                "prompt": "Generous use of negative space, minimalist composition, focus on subject, breathability",
                "tags": ["negative-space", "minimalist", "breathing-room", "focus"]
            },
            {
                "title": "Golden Ratio",
                "prompt": "Composition adhering to the golden ratio, aesthetically pleasing proportions, natural harmony",
                "tags": ["golden-ratio", "harmony", "aesthetics", "proportions"]
            },
            {
                "title": "Close-up Detail",
                "prompt": "Extreme close-up, focus on fine details, textures, intimate perspective",
                "tags": ["close-up", "detail", "texture", "intimate"]
            },
            {
                "title": "Wide Establishing Shot",
                "prompt": "Wide shot, establishing the scene and environment, expansive view, context",
                "tags": ["wide-shot", "establishing", "environment", "context"]
            },
            {
                "title": "Overhead Bird's Eye",
                "prompt": "Overhead shot, bird's eye view, top-down perspective, unique angle",
                "tags": ["overhead", "bird's-eye", "top-down", "unique-angle"]
            },
        ]
    },
}


def get_prompt_collection():
    """
    Retrieves the complete prompt collection organized by categories.
    
    Returns:
        Dictionary of prompt categories with their prompts
    """
    return PROMPT_CATEGORIES

def search_prompts(query: str, category: Optional[str] = None):
    """
    Search prompts by keyword or tag.
    
    Args:
        query: Search query string
        category: Optional category to limit search
        
    Returns:
        List of matching prompts with their categories
    """
    results = []
    query_lower = query.lower()
    
    categories_to_search = [category] if category else PROMPT_CATEGORIES.keys()
    
    for cat_key in categories_to_search:
        if cat_key not in PROMPT_CATEGORIES:
            continue
            
        cat_data = PROMPT_CATEGORIES[cat_key]
        
        for prompt_data in cat_data["prompts"]:
            # Search in title, prompt text, and tags
            if (query_lower in prompt_data["title"].lower() or
                query_lower in prompt_data["prompt"].lower() or
                any(query_lower in tag for tag in prompt_data["tags"])):
                
                results.append({
                    "category": cat_key,
                    "category_name": cat_data["name"],
                    **prompt_data
                })
    
    return results

def get_random_prompt(category: Optional[str] = None):
    """
    Get a random prompt from the collection.
    
    Args:
        category: Optional category to select from
        
    Returns:
        Random prompt dictionary
    """
    import random
    
    if category and category in PROMPT_CATEGORIES:
        cat_data = PROMPT_CATEGORIES[category]
        prompt_data = random.choice(cat_data["prompts"])
        return {
            "category": category,
            "category_name": cat_data["name"],
            **prompt_data
        }
    else:
        # Random from all categories
        cat_key = random.choice(list(PROMPT_CATEGORIES.keys()))
        cat_data = PROMPT_CATEGORIES[cat_key]
        prompt_data = random.choice(cat_data["prompts"])
        return {
            "category": cat_key,
            "category_name": cat_data["name"],
            **prompt_data
        }
