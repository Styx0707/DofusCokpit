on(construct){
   while(true)
   {
      if(!ord("\x06"))
      {
         if(false)
         {
            break;
         }
      }
      else
      {
         §§push("\x04");
      }
      if(!ord(§§pop()))
      {
         break;
      }
      autoLoad = true;
      centerContent = false;
      contentPath = "clips/evenementials/season/1/ui/1.swf";
      enabled = false;
      §§push("fallbackContentPath");
      §§push("");
      if(!ord("\x05"))
      {
         §§goto(addr212d7);
      }
      break;
   }
   set(§§pop(),§§pop());
   forceReload = false;
   scaleContent = false;
   styleName = "default";
   addr212d7:
   §§pop()();
}
